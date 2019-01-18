
SHELL = /bin/bash

all: package deploy

package:
	docker build --tag remotepixeltiler:latest .
	docker run -w /var/task/ --name remotepixeltiler -itd remotepixeltiler:latest /bin/bash
	docker cp remotepixeltiler:/tmp/package.zip package.zip
	docker stop remotepixeltiler
	docker rm remotepixeltiler

test-landsat:
	docker build --tag remotepixeltiler:latest .
	docker run \
		-w /var/task/ \
		--name remotepixeltiler \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
	  --env GDAL_HTTP_VERSION=2 \
	  --env TOKEN="yo" \
	  --env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.ovr" \
		-itd \
		remotepixeltiler:latest /bin/bash
	docker exec -it remotepixeltiler bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it remotepixeltiler bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.landsat import APP; print(APP({"path": "/bounds/LC80230312016320LGN00", "queryStringParameters": {"access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.landsat import APP; print(APP({"path": "/metadata/LC80230312016320LGN00", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.landsat import APP; print(APP({"path": "/processing/LC80230312016320LGN00/8/65/94.png", "queryStringParameters": {"ratio":"(b5-b4)/(b5+b4)", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.landsat import APP; print(APP({"path": "/tiles/LC80230312016320LGN00/8/65/94.png", "queryStringParameters": {"rgb":"5,3,2", "histo":"722,5088;859,4861;1164,5204", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker stop remotepixeltiler
	docker rm remotepixeltiler


test-cbers:
	docker build --tag remotepixeltiler:latest .
	docker run \
		-w /var/task/ \
		--name remotepixeltiler \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-east-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
	  --env GDAL_HTTP_VERSION=2 \
		--env TOKEN="yo" \
		--env GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR" \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF" \
	  --env AWS_REQUEST_PAYER="requester" \
		-itd \
		remotepixeltiler:latest /bin/bash
	docker exec -it remotepixeltiler bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it remotepixeltiler bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.cbers import APP; print(APP({"path": "/search", "queryStringParameters": {"row": "057", "path": "094", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.cbers import APP; print(APP({"path": "/bounds/CBERS_4_MUX_20171121_057_094_L2", "queryStringParameters": {"access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.cbers import APP; print(APP({"path": "/metadata/CBERS_4_MUX_20171121_057_094_L2", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.cbers import APP; print(APP({"path": "/processing/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png", "queryStringParameters": {"ratio":"(b8-b7)/(b8+b7)", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.cbers import APP; print(APP({"path": "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png", "queryStringParameters": {"rgb":"7,5,5", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker stop remotepixeltiler
	docker rm remotepixeltiler


test-main:
	docker build --tag remotepixeltiler:latest .
	docker run \
		-w /var/task/ \
		--name remotepixeltiler \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-east-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
	  --env GDAL_HTTP_VERSION=2 \
		--env TOKEN="yo" \
		--env GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR" \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.tif,.jp2,.vrt" \
		-itd \
		remotepixeltiler:latest /bin/bash
	docker exec -it remotepixeltiler bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it remotepixeltiler bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.main import APP; print(APP({"path": "/bounds", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.main import APP; print(APP({"path": "/processing/19/319379/270522.png", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif", "ratio":"(b3-b2)/(b3+b2)"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.main import APP; print(APP({"path": "/tiles/19/319379/270522.png", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker stop remotepixeltiler
	docker rm remotepixeltiler

#Local Test
test-sentinel:
	docker build --tag remotepixeltiler:latest .
	docker run \
		-w /var/task/ \
		--name remotepixeltiler \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_REGION=eu-central-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
	  --env GDAL_CACHEMAX=75% \
	  --env VSI_CACHE=TRUE \
	  --env VSI_CACHE_SIZE=536870912 \
	  --env CPL_TMPDIR="/tmp" \
	  --env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
	  --env GDAL_HTTP_VERSION=2 \
		--env TOKEN="yo" \
		--env GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR" \
	  --env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".jp2" \
		-itd \
		remotepixeltiler:latest /bin/bash
	docker exec -it remotepixeltiler bash -c 'unzip -q /tmp/package.zip -d /var/task'
	docker exec -it remotepixeltiler bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.sentinel import APP; print(APP({"path": "/s2/search", "queryStringParameters": {"utm":17, "grid":"NA", "lat":"S", "bbox":"-81.00082397460938,36.050209274876195,-79.77035522460938,36.73888412439432", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.sentinel import APP; print(APP({"path": "/s2/bounds/S2A_tile_20161202_16SDG_0", "queryStringParameters": {"access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.sentinel import APP; print(APP({"path": "/s2/metadata/S2A_tile_20161202_16SDG_0", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker exec -it remotepixeltiler python3 -c 'from remotepixel_tiler.sentinel import APP; print(APP({"path": "/s2/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png", "queryStringParameters": {"rgb":"04,03,02", "histo":"256,1701:496,1498:798,1449", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker stop remotepixeltiler
	docker rm remotepixeltiler


deploy:
	sls deploy --sat cbers
	sls deploy --sat landsat
	sls deploy --sat sentinel
	sls deploy --sat main

clean:
	docker stop remotepixeltiler
	docker rm remotepixeltiler
