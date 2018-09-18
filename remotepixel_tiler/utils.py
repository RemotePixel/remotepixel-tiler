"""app.sentinel: handle request for Sentinel-tiler."""

import requests
import datetime
from urllib.parse import urlencode

opensearchurl = "http://opensearch.sentinel-hub.com/resto/api/collections"


def zeroPad(n, l):
    """Add leading 0."""
    return str(n).zfill(l)


def sentinel2_search(
    bbox,
    utm=None,
    lat=None,
    grid=None,
    start_date="2016-01-01",
    end_date=None,
    max_cloud=100,
):
    """Search."""
    if not end_date:
        end_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

    params = {}
    params.update(
        dict(startDate=start_date, completionDate=end_date, box=bbox, maxRecords=500)
    )

    start_index = 1
    while True:
        params["index"] = start_index

        p = urlencode(params)
        url = f"{opensearchurl}/Sentinel2/search.json?{p}"
        r = requests.get(url).json()

        for tile_info in r["features"]:
            properties = tile_info["properties"]
            s3Path = properties["s3Path"]
            utm_zone = zeroPad(s3Path.split("/")[1], 2)
            latitude_band = s3Path.split("/")[2]
            grid_square = s3Path.split("/")[3]

            if utm is not None and int(utm_zone) != int(utm):
                continue

            if lat is not None and latitude_band != lat:
                continue

            if grid is not None and grid_square != grid:
                continue

            num = s3Path.split("/")[-1]

            sp = properties["spacecraft"]
            acquisition_date = datetime.datetime.strptime(
                properties["startDate"], "%Y-%m-%dT%H:%M:%SZ"
            ).strftime("%Y%m%d")

            cloud_coverage = properties.get("cloudCover", 0)
            if cloud_coverage > max_cloud:
                continue

            info = {
                "sat": sp,
                "path": s3Path,
                "utm_zone": utm_zone,
                "latitude_band": latitude_band,
                "grid_square": grid_square,
                "num": num,
                "acquisition_date": acquisition_date,
                "fulldate": properties["startDate"],
                "geometry": tile_info.get("geometry"),
                # "coverage": tile_info.get("dataCoveragePercentage")
                "cloud_coverage": cloud_coverage,
                "snow_coverage": properties.get("snowCover", 0),
                "productIdentifier": properties["productIdentifier"],
                "browseURL": f"https://roda.sentinel-hub.com/sentinel-s2-l1c/{s3Path}/preview.jpg",
                "infoURL": f"https://roda.sentinel-hub.com/sentinel-s2-l1c/{s3Path}/tileInfo.json",
                "productURL": f"https://roda.sentinel-hub.com/sentinel-s2-l1c/{s3Path}/productInfo.json",
            }

            info[
                "scene_id"
            ] = f"{sp}_tile_{acquisition_date}_{utm_zone}{latitude_band}{grid_square}_{num}"
            yield info

        if len(r["features"]) < 500:
            break

        start_index += 500
