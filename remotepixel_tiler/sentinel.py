"""app.sentinel: handle request for Sentinel-tiler."""

from typing import Any, Dict, Tuple, Union, BinaryIO

import json
import urllib

import rasterio
from rasterio import warp
from rio_tiler import sentinel2
from rio_tiler.mercator import get_zooms
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import array_to_image, get_colormap, expression

from remotepixel_tiler.utils import _postprocess

from lambda_proxy.proxy import API

APP = API(name="sentinel-tiler")


class SentinelTilerError(Exception):
    """Base exception class."""


@APP.route(
    "/s2/<scene>.json",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
@APP.route(
    "/s2/tilejson.json",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
@APP.pass_event
def tilejson_handler(
    event: Dict,
    scene: str,
    tile_format: str = "png",
    tile_scale: int = 1,
    **kwargs: Any,
) -> Tuple[str, str, str]:
    """Handle /tilejson.json requests."""
    # HACK
    token = event["multiValueQueryStringParameters"].get("access_token")
    if token:
        kwargs.update(dict(access_token=token[0]))

    qs = urllib.parse.urlencode(list(kwargs.items()))
    tile_url = f"{APP.host}/s2/tiles/{scene}/{{z}}/{{x}}/{{y}}@{tile_scale}x.{tile_format}?{qs}"

    scene_params = sentinel2._sentinel_parse_scene_id(scene)
    sentinel_address = "s3://{}/{}/B{}.jp2".format(
        sentinel2.SENTINEL_BUCKET, scene_params["key"], "04"
    )
    with rasterio.open(sentinel_address) as src_dst:
        bounds = warp.transform_bounds(
            *[src_dst.crs, "epsg:4326"] + list(src_dst.bounds), densify_pts=21
        )
        minzoom, maxzoom = get_zooms(src_dst)
        center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, minzoom]

    meta = dict(
        bounds=bounds,
        center=center,
        minzoom=minzoom,
        maxzoom=maxzoom,
        name=scene,
        tilejson="2.1.0",
        tiles=[tile_url],
    )
    return ("OK", "application/json", json.dumps(meta))


@APP.route(
    "/s2/bounds/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
def bounds(scene: str) -> Tuple[str, str, str]:
    """Handle bounds requests."""
    return ("OK", "application/json", json.dumps(sentinel2.bounds(scene)))


@APP.route(
    "/s2/metadata/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
def metadata(
    scene: str, pmin: Union[str, float] = 2., pmax: Union[str, float] = 98.
) -> Tuple[str, str, str]:
    """Handle metadata requests."""
    pmin = float(pmin) if isinstance(pmin, str) else pmin
    pmax = float(pmax) if isinstance(pmax, str) else pmax
    info = sentinel2.metadata(scene, pmin, pmax)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/s2/tiles/<scene>/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["tiles"],
)
@APP.route(
    "/s2/tiles/<scene>/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["tiles"],
)
def tile(
    scene: str,
    z: int,
    x: int,
    y: int,
    scale: int = 1,
    ext: str = "png",
    bands: str = None,
    expr: str = None,
    rescale: str = None,
    color_formula: str = None,
    color_map: str = None,
) -> Tuple[str, str, BinaryIO]:
    """Handle tile requests."""
    driver = "jpeg" if ext == "jpg" else ext

    if bands and expr:
        raise SentinelTilerError("Cannot pass bands and expression")

    tilesize = scale * 256

    if expr is not None:
        tile, mask = expression(scene, x, y, z, expr, tilesize=tilesize)

    elif bands is not None:
        tile, mask = sentinel2.tile(
            scene, x, y, z, bands=tuple(bands.split(",")), tilesize=tilesize
        )
    else:
        raise SentinelTilerError("No bands nor expression given")

    rtile, rmask = _postprocess(
        tile, mask, rescale=rescale, color_formula=color_formula
    )

    if color_map:
        color_map = get_colormap(color_map, format="gdal")

    options = img_profiles.get(driver, {})
    return (
        "OK",
        f"image/{ext}",
        array_to_image(rtile, rmask, img_format=driver, color_map=color_map, **options),
    )


@APP.route("/favicon.ico", methods=["GET"], cors=True, tag=["other"])
def favicon() -> Tuple[str, str, str]:
    """Favicon."""
    return ("EMPTY", "text/plain", "")
