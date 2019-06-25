"""app.sentinel: handle request for Sentinel-tiler."""

from typing import Tuple, Union
from typing.io import BinaryIO

import json

from rio_tiler import sentinel2
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import array_to_image, get_colormap, expression

from remotepixel_tiler.utils import _postprocess

from lambda_proxy.proxy import API

APP = API(name="sentinel-tiler")


class SentinelTilerError(Exception):
    """Base exception class."""


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
