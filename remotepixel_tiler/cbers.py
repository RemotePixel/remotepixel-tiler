"""app.cbers: handle request for CBERS-tiler."""

import json

from rio_tiler import cbers
from rio_tiler.profiles import img_profiles
from rio_tiler.utils import array_to_image, get_colormap, expression
from aws_sat_api.search import cbers as cbers_search

from .utils import _postprocess

from lambda_proxy.proxy import API

APP = API(app_name="cbers-tiler")


class CbersTilerError(Exception):
    """Base exception class."""


@APP.route(
    "/search/<string:path>/<string:row>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def search(path, row):
    """Handle search requests."""
    if not path:
        raise CbersTilerError("Missing 'path' parameter")
    if not row:
        raise CbersTilerError("Missing 'row' parameter")

    data = list(cbers_search(path, row))
    info = {
        "request": {"path": path, "row": row},
        "meta": {"found": len(data)},
        "results": data,
    }

    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/bounds/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def bounds(scene):
    """Handle bounds requests."""
    info = cbers.bounds(scene)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/metadata/<scene>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def metadata(scene, pmin=2, pmax=98):
    """Handle metadata requests."""
    pmin = float(pmin) if isinstance(pmin, str) else pmin
    pmax = float(pmax) if isinstance(pmax, str) else pmax

    info = cbers.metadata(scene, pmin, pmax)
    return ("OK", "application/json", json.dumps(info))


@APP.route(
    "/tiles/<scene>/<int:z>/<int:x>/<int:y>.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
@APP.route(
    "/tiles/<scene>/<int:z>/<int:x>/<int:y>@<int:scale>x.<ext>",
    methods=["GET"],
    cors=True,
    token=True,
    payload_compression_method="gzip",
    binary_b64encode=True,
)
def tile(
    scene,
    z,
    x,
    y,
    scale=1,
    ext="png",
    bands=None,
    expr=None,
    rescale=None,
    color_formula=None,
    color_map=None,
):
    """Handle tile requests."""
    if ext == "jpg":
        driver = "jpeg"
    elif ext == "jp2":
        driver = "JP2OpenJPEG"
    else:
        driver = ext

    if bands and expr:
        raise CbersTilerError("Cannot pass bands and expression")
    if not bands and not expr:
        raise CbersTilerError("Need bands or expression")

    if bands:
        bands = tuple(bands.split(","))

    tilesize = scale * 256

    if expr is not None:
        tile, mask = expression(scene, x, y, z, expr, tilesize=tilesize)
    elif bands is not None:
        tile, mask = cbers.tile(scene, x, y, z, bands=bands, tilesize=tilesize)

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
