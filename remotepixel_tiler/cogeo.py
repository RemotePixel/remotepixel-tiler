"""app.main: handle request for lambda-tiler."""

from typing import Any, BinaryIO, Tuple, Union

import os
import re
import json
import urllib

import numpy

from rio_tiler import main

import rasterio
from rasterio import warp

from rio_tiler.profiles import img_profiles
from rio_tiler.mercator import get_zooms
from rio_tiler.utils import array_to_image, get_colormap, expression
from remotepixel_tiler.utils import _postprocess
from lambda_proxy.proxy import API


APP = API(name="cogeo-tiler")


class TilerError(Exception):
    """Base exception class."""


@APP.route(
    "/tilejson.json",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
def tilejson_handler(
    url: str, tile_format: str = "png", tile_scale: int = 1, **kwargs: Any
) -> Tuple[str, str, str]:
    """Handle /tilejson.json requests."""
    kwargs.update(dict(url=url))
    qs = urllib.parse.urlencode(list(kwargs.items()))
    tile_url = f"{APP.host}/tiles/{{z}}/{{x}}/{{y}}@{tile_scale}x.{tile_format}"
    if qs:
        tile_url += f"?{qs}"

    with rasterio.open(url) as src_dst:
        bounds = warp.transform_bounds(
            src_dst.crs, "epsg:4326", *src_dst.bounds, densify_pts=21
        )
        minzoom, maxzoom = get_zooms(src_dst)
        center = [(bounds[0] + bounds[2]) / 2, (bounds[1] + bounds[3]) / 2, minzoom]

    meta = dict(
        bounds=bounds,
        center=center,
        minzoom=minzoom,
        maxzoom=maxzoom,
        name=os.path.basename(url),
        tilejson="2.1.0",
        tiles=[tile_url],
    )
    return ("OK", "application/json", json.dumps(meta))


@APP.route(
    "/bounds",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
def bounds(url: str) -> Tuple[str, str, str]:
    """Handle bounds requests."""
    info = main.bounds(url)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/metadata",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["metadata"],
)
def metadata(
    url: str, pmin: Union[str, float] = 2., pmax: Union[str, float] = 98.
) -> Tuple[str, str, str]:
    """Handle bounds requests."""
    pmin = float(pmin) if isinstance(pmin, str) else pmin
    pmax = float(pmax) if isinstance(pmax, str) else pmax
    info = main.metadata(url, pmin=pmin, pmax=pmax)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/tiles/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["tiles"],
)
@APP.route(
    "/tiles/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
    ttl=3600,
    tag=["tiles"],
)
def tile(
    z: int,
    x: int,
    y: int,
    scale: int = 1,
    ext: str = None,
    url: str = None,
    indexes: Union[str, Tuple[int]] = None,
    expr: str = None,
    nodata: Union[str, int, float] = None,
    rescale: str = None,
    color_formula: str = None,
    color_map: str = None,
) -> Tuple[str, str, BinaryIO]:
    """Handle tile requests."""
    driver = "jpeg" if ext == "jpg" else ext

    if indexes and expr:
        raise TilerError("Cannot pass indexes and expression")

    if not url:
        raise TilerError("Missing 'url' parameter")

    if isinstance(indexes, str):
        indexes = tuple(int(s) for s in re.findall(r"\d+", indexes))

    if nodata is not None:
        nodata = numpy.nan if nodata == "nan" else float(nodata)

    tilesize = scale * 256

    if expr is not None:
        tile, mask = expression(
            url, x, y, z, expr=expr, tilesize=tilesize, nodata=nodata
        )
    else:
        tile, mask = main.tile(
            url, x, y, z, indexes=indexes, tilesize=tilesize, nodata=nodata
        )

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
