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

$ make package && make test

# Install serverless and plugin
$ npm install
```

You can deploy each tiler independantly

```bash
$ SECRET_TOKEN=mytoken cd services/landsat && sls deploy --bucket my-bucket
Note: `my-bucket` has to be in us-west-2 region

$ SECRET_TOKEN=mytoken cd services/cbers && sls deploy --stage production --bucket my-bucket
Note: `my-bucket` has to be in us-east-1 region

$ SECRET_TOKEN=mytoken  cd services/sentinel && sls deploy --bucket my-bucket 
Note: `my-bucket` has to be in eu-central-1 region

$ cd services/cogeo && sls deploy --bucket my-bucket --region us-east-1
Note: `my-bucket` has to be in the same region
```

### API Docs:
- cogeo: https://cogeo.remotepixel.ca/docs
- landsat: https://landsat.remotepixel.ca/docs
- cbers: https://cbers.remotepixel.ca/docs

#### Infos & links
- [rio-tiler](https://github.com/mapbox/rio-tiler) rasterio plugin that process Landsat data hosted on AWS S3.
- [landsat-tiler](https://github.com/mapbox/landsat-tiler)
- [sentinel-tiler](https://github.com/mapbox/sentinel-tiler)
- [cbers-tiler](https://github.com/mapbox/cbers-tiler)
