"""tests remotepixel_tiler.cbers."""

import json
import pytest

from remotepixel_tiler.cbers import APP


@pytest.fixture(autouse=True)
def testing_env_var(monkeypatch):
    """Set env."""
    monkeypatch.setenv("TOKEN", "YO")
    monkeypatch.setenv("AWS_REQUEST_PAYER", "requester")


@pytest.fixture()
def event():
    """Event fixture."""
    return {
        "path": "/",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }


def test_search(event):
    """Should work as expected (search data)."""
    event["path"] = "/search"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"row": "108", "path": "168", "access_token": "YO"}

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

    event["path"] = "/search"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"row": "108", "access_token": "YO"}
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "Missing 'path' parameter"

    event["path"] = "/search"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"path": "108", "access_token": "YO"}
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "Missing 'row' parameter"


def test_bounds(event):
    """Should work as expected (get bounds)."""
    event["path"] = "/bounds/CBERS_4_MUX_20171121_057_094_L2"
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
    event["path"] = "/metadata/CBERS_4_MUX_20171121_057_094_L2"
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


def test_tiles_error(event):
    """Should work as expected (get metadata)."""
    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
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

    event["path"] = "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png"
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
    """Should work as expected (get metadata)."""
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
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]

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
    """Should work as expected (get metadata)."""
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
        "Content-Encoding": "gzip",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
