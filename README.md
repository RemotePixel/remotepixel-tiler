# remotepixel-tiler

[![CircleCI](https://circleci.com/gh/RemotePixel/remotepixel-tiler.svg?style=svg)](https://circleci.com/gh/RemotePixel/remotepixel-tiler)

[![codecov](https://codecov.io/gh/RemotePixel/remotepixel-tiler/branch/master/graph/badge.svg)](https://codecov.io/gh/RemotePixel/remotepixel-tiler)

Sentinel / Landsat / CBERS / COGEO Serverless dynamic tiler

Bundle of `landsat-tiler`, `sentinel-tiler`, `cbers-tiler` and `cogeo-tiler` powering RemotePixel [viewer](https://viewer.remotepixel.ca).

![viewer](https://user-images.githubusercontent.com/10407788/34139036-873c23e2-e440-11e7-9699-a2da6046a494.jpg)

# Deployment

##### Requirement
  - AWS Account
  - Docker
  - npm/node + Serverless

```bash
#Clone the repo
$ git clone https://github.com/RemotePixel/remotepixel-tiler.git
$ cd remotepixel-tiler/


$ docker login

# Fetch Amazon linux AMI docker container + Install Python modules + create package
# Create package using custom GDAL install
$ make package && make test

# Install serverless and plugin
$ npm install

# Deploy landsat, cogeo and cbers lambda functions
$ SECRET_TOKEN=mytoken make deploy
```

You can deploy each tiler independantly

```bash
$ SECRET_TOKEN=mytoken cd services/landsat && sls deploy --stage production
```

#### Infos & links
- [rio-tiler](https://github.com/mapbox/rio-tiler) rasterio plugin that process Landsat data hosted on AWS S3.
- [landsat-tiler](https://github.com/mapbox/landsat-tiler)
- [sentinel-tiler](https://github.com/mapbox/sentinel-tiler)
- [cbers-tiler](https://github.com/mapbox/cbers-tiler)
