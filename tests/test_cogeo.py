"""tests remotepixel_tiler.landsat."""

import os
import json

import numpy

import pytest
from mock import patch

from remotepixel_tiler.cogeo import APP

metadata_results = os.path.join(
    os.path.dirname(__file__), "fixtures", "metadata_cogeo.json"
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


@pytest.fixture()
def event():
    """Event fixture."""
    return {
        "path": "/",
        "httpMethod": "GET",
        "headers": {},
        "queryStringParameters": {},
    }


@patch("remotepixel_tiler.cogeo.main")
def test_bounds(cogeo, event):
    """Should work as expected (get bounds)."""
    cogeo.bounds.return_value = {
        "url": "https://a-totally-fake-url.fake/my.tif",
        "bounds": [
            39.28650720617372,
            -5.770217424643658,
            39.313619221090086,
            -5.743046418788738,
        ],
    }

    event["path"] = "/bounds"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"url": "https://a-totally-fake-url.fake/my.tif"}

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


@patch("remotepixel_tiler.cogeo.main")
def test_noUrl(cogeo, event):
    """Should work as expected (get bounds)."""

    event["path"] = "/bounds"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {}

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


@patch("remotepixel_tiler.cogeo.main")
def test_metadata(cogeo, event):
    """Should work as expected (get metadata)."""
    cogeo.metadata.return_value = metadata_results

    event["path"] = "/metadata"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {"url": "https://a-totally-fake-url.fake/my.tif"}

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
    assert len(result["statistics"].keys()) == 3


@patch("remotepixel_tiler.cogeo.main")
def test_tiles_error(cogeo, event):
    """Should work as expected (raise errors)."""
    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "indexes": "1",
        "expr": "1",
        "url": "https://a-totally-fake-url.fake/my.tif",
    }

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
    assert result["errorMessage"] == "Cannot pass indexes and expression"
    cogeo.assert_not_called()

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {}

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Cache-Control": "max-age=3600",
        "Content-Type": "application/json",
    }
    statusCode = 500

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    result = json.loads(res["body"])
    assert result["errorMessage"] == "Missing 'url' parameter"
    cogeo.assert_not_called()


@patch("remotepixel_tiler.cogeo.main")
@patch("remotepixel_tiler.cogeo.expression")
def test_tiles_expr(expression, cogeo, event):
    """Should work as expected (get tile)."""
    tilesize = 256
    tile = numpy.random.rand(1, tilesize, tilesize)
    mask = numpy.full((tilesize, tilesize), 255)

    expression.return_value = (tile, mask)

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://a-totally-fake-url.fake/my.tif",
        "expr": "(b1-b2)/(b1+b2)",
        "rescale": "-1,1",
        "color_map": "cfastie",
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
    cogeo.assert_not_called()

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "url": "https://a-totally-fake-url.fake/my.tif",
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
        "Cache-Control": "max-age=3600",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    cogeo.assert_not_called()


@patch("remotepixel_tiler.cogeo.main")
@patch("remotepixel_tiler.cogeo.expression")
def test_tiles_bands(expression, cogeo, event):
    """Should work as expected (get tile)."""
    tilesize = 256
    tile = numpy.random.rand(3, tilesize, tilesize) * 1000
    mask = numpy.full((tilesize, tilesize), 255)

    cogeo.tile.return_value = (tile.astype(numpy.uint8), mask)

    event["path"] = "/tiles/19/319379/270522.png"
    event["httpMethod"] = "GET"
    event["queryStringParameters"] = {
        "indexes": "1,2,3",
        "url": "https://a-totally-fake-url.fake/my.tif",
    }
    event["headers"]["Accept-Encoding"] = "gzip, deflate"

    headers = {
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Origin": "*",
        "Content-Encoding": "gzip",
        "Cache-Control": "max-age=3600",
        "Content-Type": "image/png",
    }
    statusCode = 200

    res = APP(event, {})
    assert res["headers"] == headers
    assert res["statusCode"] == statusCode
    assert res["isBase64Encoded"]
    assert res["body"]
    expression.assert_not_called()
