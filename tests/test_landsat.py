"""tests remotepixel_tiler.landsat."""

import os
import json
import numpy

import pytest
from mock import patch

from remotepixel_tiler.landsat import APP


metadata_results = os.path.join(
    os.path.dirname(__file__), "fixtures", "metadata_landsat.json"
)
with open(metadata_results, "r") as f:
    metadata_results = json.loads(f.read())


@pytest.fixture(autouse=True)
def testing_env_var(monkeypatch):
    """Set fake env to make sure we don't hit AWS services."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "jqt")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "rde")
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.setenv("AWS_CONFIG_FILE", "/tmp/noconfigheere")
    monkeypatch.setenv("AWS_SHARED_CREDENTIALS_FILE", "/tmp/noconfighereeither")
    monkeypatch.setenv("TOKEN", "YO")


@pytest.fixture()
def event():
    """Event fixture."""
    return {
        "path": "/",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }


@patch("remotepixel_tiler.landsat.landsat8")
def test_bounds(landsat8, event):
    """Should work as expected (get bounds)."""
    landsat8.bounds.return_value = {
        "sceneid": "LC80230312016320LGN00",
        "bounds": [-89.79084, 40.65443, -86.91434, 42.83954],
    }

    event["path"] = "/bounds/LC80230312016320LGN00"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]


@patch("remotepixel_tiler.landsat.landsat8")
def test_metadata(landsat8, event):
    """Should work as expected (get metadata)."""
    landsat8.metadata.return_value = metadata_results

    event["path"] = "/metadata/LC80230312016320LGN00"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]
    assert result["statistics"]
    assert len(result["statistics"].keys()) == 11

    event["path"] = "/metadata/LC80230312016320LGN00"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"pmin": "5", "pmax": "95", "access_token": "YO"}
    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]
    assert result["statistics"]


@patch("remotepixel_tiler.landsat.landsat8")
@patch("remotepixel_tiler.landsat.expression")
def test_tiles_error(expression, landsat8, event):
    """Should work as expected (raise errors)."""
    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO", "bands": "1", "expr": "1"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "Cannot pass bands and expression"
    landsat8.assert_not_called()
    expression.assert_not_called()

    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/json",
    }
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "No bands nor expression given"
    landsat8.assert_not_called()
    expression.assert_not_called()


@patch("remotepixel_tiler.landsat.landsat8")
@patch("remotepixel_tiler.landsat.expression")
def test_tiles_expr(expression, landsat8, event):
    """Should work as expected (get tile)."""
    tilesize = 256
    tile = numpy.random.rand(1, tilesize, tilesize)
    mask = numpy.full((tilesize, tilesize), 255)

    expression.return_value = (tile, mask)

    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "expr": "(b5-b4)/(b5+b4)",
        "rescale": "-1,1",
        "color_map": "cfastie",
        "access_token": "YO",
    }

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    expression.call_with(
        "LC80230312016320LGN00", 8, 65, 94, "(b5-b4)/(b5+b4)", tilesize=256, pan=False
    )
    landsat8.assert_not_called()

    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "expr": "(b5-b4)/(b5+b4)",
        "rescale": "-1,1",
        "color_map": "cfastie",
        "access_token": "YO",
    }
    event["headers"]["Accept-Encoding"] = "gzip, deflate"

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Encoding": "gzip",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    landsat8.assert_not_called()


@patch("remotepixel_tiler.landsat.landsat8")
@patch("remotepixel_tiler.landsat.expression")
def test_tiles_bands(expression, landsat8, event):
    """Should work as expected (get tile)."""
    tilesize = 256
    tile = (numpy.random.rand(3, tilesize, tilesize) * 10000).astype(numpy.uint16)
    mask = numpy.full((tilesize, tilesize), 255)

    landsat8.tile.return_value = (tile, mask)

    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "bands": "5,3,2",
        "color_formula": "gamma RGB 3.5 saturation 1.7 sigmoidal RGB 15 0.35",
        "access_token": "YO",
    }
    event["headers"]["Accept-Encoding"] = "gzip, deflate"
    print(event)
    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Encoding": "gzip",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    expression.assert_not_called()
    landsat8.call_with(
        "LC80230312016320LGN00",
        8,
        65,
        94,
        bands=("5", "4", "3"),
        tilesize=256,
        pan=False,
    )

    tilesize = 512
    tile = (numpy.random.rand(3, tilesize, tilesize) * 10000).astype(numpy.uint16)
    mask = numpy.full((tilesize, tilesize), 255)

    landsat8.tile.return_value = (tile, mask)

    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94@2x.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "bands": "5,3,2",
        "color_formula": "gamma RGB 3.5 saturation 1.7 sigmoidal RGB 15 0.35",
        "access_token": "YO",
    }

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    expression.assert_not_called()
    landsat8.call_with(
        "LC80230312016320LGN00",
        8,
        65,
        94,
        bands=("5", "4", "3"),
        tilesize=512,
        pan=False,
    )
