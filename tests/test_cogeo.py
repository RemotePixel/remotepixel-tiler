"""tests remotepixel_tiler.landsat."""

import json
import pytest

from remotepixel_tiler.cogeo import APP


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
    event["path"] = "/bounds"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"
    }

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
    event["path"] = "/metadata"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"
    }

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
    assert len(result["statistics"].keys()) == 3


def test_tiles_error(event):
    """Should work as expected (raise errors)."""
    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "indexes": "1",
        "expr": "1",
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif",
    }

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
    assert result["errorMessage"] == "Cannot pass indexes and expression"

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {}

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
    assert result["errorMessage"] == "Missing 'url' parameter"


def test_tiles_expr(event):
    """Should work as expected (get tile)."""
    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif",
        "expr": "(b1-b2)/(b1+b2)",
        "rescale": "-1,1",
        "color_map": "cfastie",
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

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif",
        "expr": "(b1-b2)/(b1+b1)",
        "rescale": "-1,1",
        "color_map": "cfastie",
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
    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"
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
