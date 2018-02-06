# remotepixel-tiler
Sentinel / Landsat / CBERS serverless tile server

Bundle of `landsat-tiler`, `sentinel-tiler` and `cbers-tiler` powering RemotePixel [viewer](https://viewer.remotepixel.ca).

![viewer](https://user-images.githubusercontent.com/10407788/34139036-873c23e2-e440-11e7-9699-a2da6046a494.jpg)

# Features
While the lambda function are the same is found in the original repo (landsat-tiler ...) I haded two features:
- Alarms: get mail notifcation when something is not right  
- Token: pseudo secure endpoint using user defined Token

# Installation

##### Requirement
  - AWS Account
  - Docker
  - node + npm

##### Configuration

```bash
#Clone the repo
git clone https://github.com/RemotePixel/remotepixel-tiler.git
cd remotepixel-tiler/

# set Token and Email
vi config.json
{"token": "this is a token I defined", "mail": "your@email.com"}

# Fetch Amazon linux AMI docker container + Install Python modules + create package
# Create package using rasterio wheel
make wheel

# Create package using custom GDAL install
make custom

# Deploy sentinel, landsat and cbers lambda functions
make deploy
```



#### Infos & links
- [rio-tiler](https://github.com/mapbox/rio-tiler) rasterio plugin that process Landsat data hosted on AWS S3.
- [landsat-tiler](https://github.com/mapbox/landsat-tiler)
- [sentinel-tiler](https://github.com/mapbox/sentinel-tiler)
- [cbers-tiler](https://github.com/mapbox/cbers-tiler)
