"""app.sentinel: handle request for Sentinel-tiler."""

import re
import json

import numpy as np

from rio_tiler import sentinel2
from rio_tiler.utils import (
    array_to_img,
    linear_rescale,
    get_colormap,
    expression,
    b64_encode_img,
)

from remotepixel_tiler.utils import sentinel2_search

from lambda_proxy.proxy import API

APP = API(app_name="sentinel-tiler")


class SentinelTilerError(Exception):
    """Base exception class."""


@APP.route("/s2/search", methods=["GET"], cors=True, token=True)
def search(bbox=None, **kwargs):
    """Handle search requests."""
    if not bbox:
        raise SentinelTilerError("Missing 'bbox' parameter")

    data = list(sentinel2_search(bbox, **kwargs))
    info = {
        "request": {"bbox": bbox, **kwargs},
        "meta": {"found": len(data)},
        "results": data,
    }

    return ("OK", "application/json", json.dumps(info))


@APP.route("/s2/bounds/<scene>", methods=["GET"], cors=True, token=True)
def bounds(scene):
    """Handle bounds requests."""
    info = sentinel2.bounds(scene)
    return ("OK", "application/json", json.dumps(info))


@APP.route("/s2/metadata/<scene>", methods=["GET"], cors=True, token=True)
def metadata(scene, pmin=2, pmax=98):
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
)
def tile(
    scene, tile_z, tile_x, tile_y, tileformat, rgb="04,03,02", histo=None, tile=256
):
    """Handle tile requests."""
    if tileformat == "jpg":
        tileformat = "jpeg"

    bands = tuple(re.findall(r"\d+", rgb))

    if not histo:
        histo = ";".join(["0,16000"] * len(bands))
    histoCut = re.findall(r"\d+,\d+", histo)
    histoCut = list(map(lambda x: list(map(int, x.split(","))), histoCut))

    if len(bands) != len(histoCut):
        raise SentinelTilerError(
            "The number of bands doesn't match the number of histogramm values"
        )

    tilesize = int(tile) if isinstance(tile, str) else tile

    tile, mask = sentinel2.tile(scene, tile_x, tile_y, tile_z, bands, tilesize=tilesize)

    rtile = np.zeros((len(bands), tilesize, tilesize), dtype=np.uint8)
    for bdx in range(len(bands)):
        rtile[bdx] = np.where(
            mask,
            linear_rescale(tile[bdx], in_range=histoCut[bdx], out_range=[0, 255]),
            0,
        )
    img = array_to_img(rtile, mask=mask)
    str_img = b64_encode_img(img, tileformat)
    return ("OK", f"image/{tileformat}", str_img)


@APP.route(
    "/s2/processing/<scene>/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
)
def ratio(
    scene, tile_z, tile_x, tile_y, tileformat, ratio=None, range=[-1, 1], tile=256
):
    """Handle processing requests."""
    if tileformat == "jpg":
        tileformat = "jpeg"

    if not ratio:
        raise SentinelTilerError("Missing 'ratio' parameter")

    tilesize = int(tile) if isinstance(tile, str) else tile

    tile, mask = expression(scene, tile_x, tile_y, tile_z, ratio, tilesize=tilesize)
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
