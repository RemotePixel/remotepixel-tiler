"""tests remotepixel_tiler.landsat."""

import json
import pytest

from remotepixel_tiler.sentinel import APP


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


def test_bounds(event):
    """Should work as expected (get bounds)."""
    event["path"] = "/s2/bounds/S2A_tile_20161202_16SDG_0"
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


# def test_metadata(event):
#     """Should work as expected (get metadata)."""
#     event["path"] = "/s2/metadata/S2A_tile_20161202_16SDG_0"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {"access_token": "YO"}
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Type": "application/json",
#     }
#     statusCode = 200
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     result = json.loads(res["body"])
#     assert result["bounds"]
#     assert result["statistics"]
#     assert len(result["statistics"].keys()) == 13
#
#     event["path"] = "/s2/metadata/S2A_tile_20161202_16SDG_0"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {"pmin": "5", "pmax": "95", "access_token": "YO"}
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     result = json.loads(res["body"])
#     assert result["bounds"]
#     assert result["statistics"]
#
#
# def test_tiles_error(event):
#     """Should work as expected (raise error)."""
#     event["path"] = "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {
#         "access_token": "YO",
#         "bands": "01",
#         "expr": "01",
#     }
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Type": "application/json",
#     }
#     statusCode = 500
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     result = json.loads(res["body"])
#     assert result["errorMessage"] == "Cannot pass bands and expression"
#
#     event["path"] = "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {
#         "access_token": "YO",
#     }
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Type": "application/json",
#     }
#     statusCode = 500
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     result = json.loads(res["body"])
#     assert result["errorMessage"] == "Need bands or expression"
#
#
# def test_tiles_expr(event):
#     """Should work as expected (get tile)."""
#     event["path"] = "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {
#         "expr": "(b5-b4)/(b5+b4)",
#         "rescale": "-1,1",
#         "color_map": "cfastie",
#         "access_token": "YO"
#     }
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Type": "image/png",
#     }
#     statusCode = 200
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     assert res["isBase64Encoded"]
#     assert res["body"]
#
#     event["path"] = "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {
#         "expr": "(b04-b03)/(b03+b04)",
#         "rescale": "-1,1",
#         "color_map": "cfastie",
#         "access_token": "YO"
#     }
#     event["headers"]["Accept-Encoding"] = "gzip, deflate"
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Encoding": "gzip",
#         "Content-Type": "image/png",
#     }
#     statusCode = 200
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     assert res["isBase64Encoded"]
#     assert res["body"]
#
#
# def test_tiles_bands(event):
#     """Should work as expected (get tile)."""
#     event["path"] = "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png"
#     event["httpMethod"] = "GET"
#     event["queryStringParameters"] = {
#         "bands": "04,03,02",
#         "color_formula": "gamma RGB 3",
#         "access_token": "YO",
#     }
#     event["headers"]["Accept-Encoding"] = "gzip, deflate"
#
#     headers = {
#         "Access-Control-Allow-Credentials": "true",
#         "Access-Control-Allow-Methods": "GET",
#         "Access-Control-Allow-Origin": "*",
#         "Content-Encoding": "gzip",
#         "Content-Type": "image/png",
#     }
#     statusCode = 200
#
#     res = APP(event, {})
#     assert res["headers"] == headers
#     assert res["statusCode"] == statusCode
#     assert res["isBase64Encoded"]
#     assert res["body"]
