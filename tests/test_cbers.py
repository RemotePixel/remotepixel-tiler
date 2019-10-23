"""tests remotepixel_tiler.cbers."""

import os
import json
import numpy

import pytest
from mock import patch

from remotepixel_tiler.cbers import APP


search_results = os.path.join(
    os.path.dirname(__file__), "fixtures", "search_cbers.json"
)
with open(search_results, "r") as f:
    search_results = json.loads(f.read())

metadata_results = os.path.join(
    os.path.dirname(__file__), "fixtures", "metadata_cbers.json"
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


@patch("remotepixel_tiler.cbers.cbers_search")
def test_search(cbers_search, event):
    """Should work as expected (search data)."""

    def mockSearch():
        yield search_results["result"]

    cbers_search.return_value = mockSearch()

    event["path"] = "/search/168/108"
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
    assert result["meta"]["found"]

    event["path"] = "/search/168"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}
    statusCode = 400

    res = APP(event, {})
    assert res["statusCode"] == statusCode


@patch("remotepixel_tiler.cbers.cbers")
def test_bounds(cbers, event):
    """Should work as expected (get bounds)."""
    cbers.bounds.return_value = {
        "sceneid": "CBERS_4_MUX_20171121_057_094_L2",
        "bounds": [
            53.302020833057796,
            4.756472757234311,
            54.628483877373,
            6.025171883475984,
        ],
    }

    event["path"] = "/bounds/CBERS_4_MUX_20171121_057_094_L2"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
        "Content-Type": "application/json",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]


@patch("remotepixel_tiler.cbers.cbers")
def test_metadata(cbers, event):
    """Should work as expected (get metadata)."""
    cbers.metadata.return_value = metadata_results

    event["path"] = "/metadata/CBERS_4_MUX_20171121_057_094_L2"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
        "Content-Type": "application/json",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]
    assert result["statistics"]
    assert len(result["statistics"].keys()) == 4

    event["path"] = "/metadata/CBERS_4_MUX_20171121_057_094_L2"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"pmin": "5", "pmax": "95", "access_token": "YO"}
    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["bounds"]
    assert result["statistics"]


@patch("remotepixel_tiler.cbers.cbers")
@patch("remotepixel_tiler.cbers.expression")
def test_tiles_error(expression, cbers, event):
    """Should work as expected (get metadata)."""
    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO", "bands": "1", "expr": "1"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "Cannot pass bands and expression"
    cbers.assert_not_called()
    expression.assert_not_called()

    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"access_token": "YO"}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
    }
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "No bands nor expression given"
    cbers.assert_not_called()
    expression.assert_not_called()


@patch("remotepixel_tiler.cbers.cbers")
@patch("remotepixel_tiler.cbers.expression")
def test_tiles_expr(expression, cbers, event):
    """Should work as expected (get metadata)."""
    tilesize = 256
    tile = numpy.random.rand(1, tilesize, tilesize)
    mask = numpy.full((tilesize, tilesize), 255)

    expression.return_value = (tile, mask)

    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "expr": "(b8-b7)/(b8+b7)",
        "rescale": "-1,1",
        "color_map": "cfastie",
        "access_token": "YO",
    }

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    cbers.assert_not_called()

    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "expr": "(b8-b7)/(b8+b7)",
        "rescale": "-1,1",
        "color_map": "cfastie",
        "access_token": "YO",
    }
    event["headers"]["Accept-Encoding"] = "gzip, deflate"

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
        "Content-Encoding": "gzip",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    cbers.assert_not_called()


@patch("remotepixel_tiler.cbers.cbers")
@patch("remotepixel_tiler.cbers.expression")
def test_tiles_bands(expression, cbers, event):
    """Should work as expected (get metadata)."""
    tilesize = 256
    tile = numpy.random.rand(3, tilesize, tilesize) * 1000
    mask = numpy.full((tilesize, tilesize), 255)

    cbers.tile.return_value = (tile.astype(numpy.uint8), mask)

    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "bands": "7,5,5",
        "color_formula": "gamma RGB 3",
        "access_token": "YO",
    }
    event["headers"]["Accept-Encoding"] = "gzip, deflate"

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
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
