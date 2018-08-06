
SHELL = /bin/bash

wheel:
	docker build -f Dockerfiles/wheel --tag lambda:latest .
	docker run -w /var/task/ --name lambda -itd lambda:latest /bin/bash
	docker cp lambda:/tmp/package.zip wheel.zip
	docker stop lambda
	docker rm lambda

custom:
	docker build -f Dockerfiles/custom --tag lambda:latest .
	docker run -w /var/task/ --name lambda -itd lambda:latest /bin/bash
	docker cp lambda:/tmp/package.zip custom.zip
	docker stop lambda
	docker rm lambda


test-landsat:
	docker build -f Dockerfiles/wheel --tag lambda:latest .
	docker run \
		-w /var/task/ \
		--name lambda \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--env TOKEN="yo" \
		-itd \
		lambda:latest /bin/bash
	docker exec -it lambda bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it lambda bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it lambda python3 -c 'from app.landsat import APP; assert APP({"path": "/bounds/LC80230312016320LGN00", "queryStringParameters": {"access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.landsat import APP; assert APP({"path": "/metadata/LC80230312016320LGN00", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.landsat import APP; assert APP({"path": "/processing/LC80230312016320LGN00/8/65/94.png", "queryStringParameters": {"ratio":"(b5-b4)/(b5+b4)", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.landsat import APP; assert APP({"path": "/tiles/LC80230312016320LGN00/8/65/94.png", "queryStringParameters": {"rgb":"5,3,2", "histo":"722,5088;859,4861;1164,5204", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker stop lambda
	docker rm lambda


test-cbers:
	docker build -f Dockerfiles/wheel --tag lambda:latest .
	docker run \
		-w /var/task/ \
		--name lambda \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_REQUEST_PAYER="requester" \
 		--env AWS_REGION=us-west-2 \
		--env PYTHONPATH=/var/task \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--env TOKEN="yo" \
		-itd \
		lambda:latest /bin/bash
	docker exec -it lambda bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it lambda bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it lambda python3 -c 'from app.cbers import APP; assert APP({"path": "/bounds/CBERS_4_MUX_20171121_057_094_L2", "queryStringParameters": {"access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.cbers import APP; assert APP({"path": "/metadata/CBERS_4_MUX_20171121_057_094_L2", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.cbers import APP; assert APP({"path": "/processing/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png", "queryStringParameters": {"ratio":"(b8-b7)/(b8+b7)", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.cbers import APP; assert APP({"path": "/tiles/CBERS_4_MUX_20171121_057_094_L2/10/664/495.png", "queryStringParameters": {"rgb":"7,5,5", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker stop lambda
	docker rm lambda


test-main:
	docker build -f Dockerfiles/wheel --tag lambda:latest .
	docker run \
		-w /var/task/ \
		--name lambda \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
 		--env AWS_REGION=us-east-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		-itd \
		lambda:latest /bin/bash
	docker exec -it lambda bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it lambda bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it lambda python3 -c 'from app.main import APP; assert APP({"path": "/bounds", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.main import APP; assert APP({"path": "/processing/19/319379/270522.png", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif", "ratio":"(b3-b2)/(b3+b2)"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.main import APP; assert APP({"path": "/tiles/19/319379/270522.png", "queryStringParameters": {"url": "https://oin-hotosm.s3.amazonaws.com/5ac626e091b5310010e0d482/0/5ac626e091b5310010e0d483.tif"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker stop lambda
	docker rm lambda

#Local Test
test-sentinel:
	docker build -f Dockerfiles/custom --tag lambda:latest .
	docker run \
		-w /var/task/ \
		--name lambda \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env AWS_REGION=eu-central-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_DATA=/var/task/share/gdal \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--env TOKEN="yo" \
		-itd \
		lambda:latest /bin/bash
	docker exec -it lambda bash -c 'unzip -q /tmp/package.zip -d /var/task'
	docker exec -it lambda bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it lambda python3 -c 'from app.sentinel import APP; assert APP({"path": "/sentinel/bounds/S2A_tile_20161202_16SDG_0", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.sentinel import APP; assert APP({"path": "/sentinel/metadata/S2A_tile_20161202_16SDG_0", "queryStringParameters": {"pmin":"2", "pmax":"99.8", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker exec -it lambda python3 -c 'from app.sentinel import APP; assert APP({"path": "/sentinel/tiles/S2A_tile_20161202_16SDG_0/10/262/397.png", "queryStringParameters": {"rgb":"04,03,02", "histo":"256,1701:496,1498:798,1449", "access_token": "yo"}, "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None)'
	docker stop lambda
	docker rm lambda


deploy:
	sls deploy --sat cbers
	sls deploy --sat landsat
	sls deploy --sat sentinel
	sls deploy --sat main

clean:
	docker stop lambda
	docker rm lambda
