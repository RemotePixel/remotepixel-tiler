"""Test ard-tiler locally."""

import click
import base64
from urllib.parse import urlparse, parse_qsl
from http.server import HTTPServer, BaseHTTPRequestHandler

from socketserver import ThreadingMixIn

from remotepixel_tiler.landsat import APP as landsat_app
from remotepixel_tiler.sentinel import APP as sentine_app
from remotepixel_tiler.cbers import APP as cbers_app
from remotepixel_tiler.cogeo import APP as cogeo_app


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    """MultiThread."""

    pass


class LandsatHandler(BaseHTTPRequestHandler):
    """Requests handler."""

    def do_GET(self):
        """Get requests."""
        q = urlparse(self.path)
        request = {
            "headers": dict(self.headers),
            "path": q.path,
            "queryStringParameters": dict(parse_qsl(q.query)),
            "httpMethod": self.command,
        }
        response = landsat_app(request, None)

        self.send_response(int(response["statusCode"]))
        for r in response["headers"]:
            self.send_header(r, response["headers"][r])
        self.end_headers()

        if response.get("isBase64Encoded"):
            response["body"] = base64.b64decode(response["body"])

        if isinstance(response["body"], str):
            self.wfile.write(bytes(response["body"], "utf-8"))
        else:
            self.wfile.write(response["body"])


class CogeoHandler(BaseHTTPRequestHandler):
    """Requests handler."""

    def do_GET(self):
        """Get requests."""
        q = urlparse(self.path)
        request = {
            "headers": dict(self.headers),
            "path": q.path,
            "queryStringParameters": dict(parse_qsl(q.query)),
            "httpMethod": self.command,
        }
        response = cogeo_app(request, None)

        self.send_response(int(response["statusCode"]))
        for r in response["headers"]:
            self.send_header(r, response["headers"][r])
        self.end_headers()

        if response.get("isBase64Encoded"):
            response["body"] = base64.b64decode(response["body"])

        if isinstance(response["body"], str):
            self.wfile.write(bytes(response["body"], "utf-8"))
        else:
            self.wfile.write(response["body"])


class CbersHandler(BaseHTTPRequestHandler):
    """Requests handler."""

    def do_GET(self):
        """Get requests."""
        q = urlparse(self.path)
        request = {
            "headers": dict(self.headers),
            "path": q.path,
            "queryStringParameters": dict(parse_qsl(q.query)),
            "httpMethod": self.command,
        }
        response = cbers_app(request, None)

        self.send_response(int(response["statusCode"]))
        for r in response["headers"]:
            self.send_header(r, response["headers"][r])
        self.end_headers()

        if response.get("isBase64Encoded"):
            response["body"] = base64.b64decode(response["body"])

        if isinstance(response["body"], str):
            self.wfile.write(bytes(response["body"], "utf-8"))
        else:
            self.wfile.write(response["body"])


class SentinelHandler(BaseHTTPRequestHandler):
    """Requests handler."""

    def do_GET(self):
        """Get requests."""
        q = urlparse(self.path)
        request = {
            "headers": dict(self.headers),
            "path": q.path,
            "queryStringParameters": dict(parse_qsl(q.query)),
            "httpMethod": self.command,
        }
        response = sentine_app(request, None)

        self.send_response(int(response["statusCode"]))
        for r in response["headers"]:
            self.send_header(r, response["headers"][r])
        self.end_headers()

        if response.get("isBase64Encoded"):
            response["body"] = base64.b64decode(response["body"])

        if isinstance(response["body"], str):
            self.wfile.write(bytes(response["body"], "utf-8"))
        else:
            self.wfile.write(response["body"])


@click.group("remotepixel_tiler")
def cli():
    """Test cli."""
    pass


@cli.command(short_help="landsat")
@click.option("--port", type=int, default=8000, help="port")
def landsat(port):
    """Launch server."""
    server_address = ("", port)
    httpd = ThreadingSimpleServer(server_address, LandsatHandler)
    click.echo(f"Starting local server at http://127.0.0.1:{port}", err=True)
    httpd.serve_forever()


@cli.command(short_help="sentinel")
@click.option("--port", type=int, default=8000, help="port")
def sentinel(port):
    """Launch server."""
    server_address = ("", port)
    httpd = ThreadingSimpleServer(server_address, SentinelHandler)
    click.echo(f"Starting local server at http://127.0.0.1:{port}", err=True)
    httpd.serve_forever()


@cli.command(short_help="cbers")
@click.option("--port", type=int, default=8000, help="port")
def cbers(port):
    """Launch server."""
    server_address = ("", port)
    httpd = ThreadingSimpleServer(server_address, CbersHandler)
    click.echo(f"Starting local server at http://127.0.0.1:{port}", err=True)
    httpd.serve_forever()


@cli.command(short_help="cogeo")
@click.option("--port", type=int, default=8000, help="port")
def cogeo(port):
    """Launch server."""
    server_address = ("", port)
    httpd = ThreadingSimpleServer(server_address, CogeoHandler)
    click.echo(f"Starting local server at http://127.0.0.1:{port}", err=True)
    httpd.serve_forever()
