"""app.main: handle request for lambda-tiler."""

import re
import json

import numpy

from rio_tiler import main
from rio_rgbify import encoders

from rio_tiler.profiles import img_profiles
from rio_tiler.utils import (
    array_to_image,
    get_colormap,
    expression,
    mapzen_elevation_rgb,
)

from .utils import _postprocess

from lambda_proxy.proxy import API

APP = API(app_name="lambda-tiler")


class TilerError(Exception):
    """Base exception class."""


@APP.route(
    "/bounds",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def bounds(url=None):
    """Handle bounds requests."""
    if not url:
        raise TilerError("Missing 'url' parameter")
    info = main.bounds(url)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/metadata",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def metadata(url=None, pmin=2, pmax=98):
    """Handle bounds requests."""
    if not url:
        raise TilerError("Missing 'url' parameter")
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
)
@APP.route(
    "/tiles/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def tile(
    z,
    x,
    y,
    scale=1,
    ext="png",
    url=None,
    indexes=None,
    expr=None,
    nodata=None,
    rescale=None,
    color_formula=None,
    color_map=None,
    dem=None,
):
    """Handle tile requests."""
    if ext == "jpg":
        driver = "jpeg"
    elif ext == "jp2":
        driver = "JP2OpenJPEG"
    else:
        driver = ext

    if indexes and expr:
        raise TilerError("Cannot pass indexes and expression")
    if not url:
        raise TilerError("Missing 'url' parameter")

    if indexes:
        indexes = tuple(int(s) for s in re.findall(r"\d+", indexes))

    tilesize = scale * 256

    if nodata is not None:
        nodata = numpy.nan if nodata == "nan" else float(nodata)

    if expr is not None:
        tile, mask = expression(url, x, y, z, expr, tilesize=tilesize)
    else:
        tile, mask = main.tile(url, x, y, z, indexes=indexes, tilesize=tilesize)

    if dem:
        if dem == "mapbox":
            tile = encoders.data_to_rgb(tile, -10000, 1)
        elif dem == "mapzen":
            tile = mapzen_elevation_rgb.data_to_rgb(tile)
        else:
            return ("NOK", "text/plain", 'Invalid "dem" mode')
    else:
        rtile, rmask = _postprocess(
            tile, mask, tilesize, rescale=rescale, color_formula=color_formula
        )

        if color_map:
            color_map = get_colormap(color_map, format="gdal")

    options = img_profiles.get(driver, {})
    return (
        "OK",
        f"image/{ext}",
        array_to_image(rtile, rmask, img_format=driver, color_map=color_map, **options),
    )


@APP.route("/favicon.ico", methods=["GET"], cors=True)
def favicon():
    """Favicon."""
    return ("NOK", "text/plain", "")
