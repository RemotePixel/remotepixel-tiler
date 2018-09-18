"""app.main: handle request for lambda-tiler."""

import re
import json

import numpy as np

from rio_tiler import main
from rio_rgbify import encoders
from rio_tiler.utils import (
    array_to_img,
    linear_rescale,
    get_colormap,
    expression,
    b64_encode_img,
    mapzen_elevation_rgb,
)

from lambda_proxy.proxy import API

APP = API(app_name="lambda-tiler")


class TilerError(Exception):
    """Base exception class."""


@APP.route("/bounds", methods=["GET"], cors=True)
def bounds(url=None):
    """Handle bounds requests."""
    if not url:
        raise TilerError("Missing 'url' parameter")
    info = main.bounds(url)
    return ("OK", "application/json", json.dumps(info))


@APP.route("/tiles/<int:z>/<int:x>/<int:y>.<ext>", methods=["GET"], cors=True)
def tile(
    tile_z,
    tile_x,
    tile_y,
    tileformat,
    url=None,
    indexes=None,
    tile=512,
    nodata=None,
    dem=None,
):
    """Handle tile requests."""
    if tileformat == "jpg":
        tileformat = "jpeg"

    if not url:
        raise TilerError("Missing 'url' parameter")

    if indexes:
        indexes = tuple(int(s) for s in re.findall(r"\d+", indexes))

    tilesize = int(tile) if isinstance(tile, str) else tile

    if nodata is not None:
        nodata = int(nodata)

    tile, mask = main.tile(
        url, tile_x, tile_y, tile_z, indexes=indexes, tilesize=tilesize, nodata=nodata
    )

    if dem:
        if dem == "mapbox":
            tile = encoders.data_to_rgb(tile, -10000, 1)
        elif dem == "mapzen":
            tile = mapzen_elevation_rgb.data_to_rgb(tile)
        else:
            return ("NOK", "text/plain", 'Invalid "dem" mode')

    img = array_to_img(tile, mask=mask)
    str_img = b64_encode_img(img, tileformat)
    return ("OK", f"image/{tileformat}", str_img)


@APP.route("/processing/<int:z>/<int:x>/<int:y>.<ext>", methods=["GET"], cors=True)
def ratio(
    tile_z, tile_x, tile_y, tileformat, url=None, ratio=None, range=[-1, 1], tile=256
):
    """Handle processing requests."""
    if tileformat == "jpg":
        tileformat = "jpeg"

    if not url:
        raise TilerError("Missing 'url' parameter")

    tilesize = int(tile) if isinstance(tile, str) else tile

    tile, mask = expression(url, tile_x, tile_y, tile_z, ratio, tilesize=tilesize)

    if len(tile.shape) == 2:
        tile = np.expand_dims(tile, axis=0)

    rtile = np.where(
        mask, linear_rescale(tile, in_range=range, out_range=[0, 255]), 0
    ).astype(np.uint8)

    img = array_to_img(rtile, color_map=get_colormap(name="cfastie"), mask=mask)
    str_img = b64_encode_img(img, tileformat)
    return ("OK", f"image/{tileformat}", str_img)


@APP.route("/favicon.ico", methods=["GET"], cors=True)
def favicon():
    """Favicon."""
    return ("NOK", "text/plain", "")
