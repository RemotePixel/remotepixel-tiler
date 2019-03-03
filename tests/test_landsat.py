"""tests remotepixel_tiler.landsat."""

import json
import pytest

from remotepixel_tiler.landsat import APP


@pytest.fixture(autouse=True)
def testing_env_var(monkeypatch):
    """Set env."""
    monkeypatch.setenv("TOKEN", "YO")
    monkeypatch.setenv("GDAL_DISABLE_READDIR_ON_OPEN", "TRUE")
    monkeypatch.setenv("CPL_VSIL_CURL_ALLOWED_EXTENSIONS", ".TIF,.ovr")


@pytest.fixture()
def event():
    """Event fixture."""
    return {
        "path": "/",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }


def test_bounds(event):
    """Should work as expected (get bounds)."""
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


def test_metadata(event):
    """Should work as expected (get metadata)."""
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


def test_tiles_error(event):
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
    assert result["errorMessage"] == "Need bands or expression"


def test_tiles_expr(event):
    """Should work as expected (get tile)."""
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


def test_tiles_bands(event):
    """Should work as expected (get tile)."""
    event["path"] = "/tiles/LC80230312016320LGN00/8/65/94.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "bands": "5,3,2",
        "color_formula": "gamma RGB 3",
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
