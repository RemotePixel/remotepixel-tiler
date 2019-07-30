
SHELL = /bin/bash

all: package test

package:
	docker build --tag remotepixeltiler:latest .
	docker run \
		--name remotepixeltiler \
		-w /tmp \
		--volume $(shell pwd)/bin:/tmp/bin \
		--volume $(shell pwd)/:/local \
		--env PACKAGE_TMP=/tmp/package \
		--env PACKAGE_PATH=/local/package.zip \
		-itd remotepixeltiler:latest \
		bash
	docker exec -it remotepixeltiler bash '/tmp/bin/package.sh'
	docker stop remotepixeltiler
	docker rm remotepixeltiler

test:
	docker run \
		--name lambda \
		-w /var/task/ \
		--volume $(shell pwd)/bin:/tmp/bin \
		--volume $(shell pwd)/:/local \
		--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
		--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
		--env GDAL_DATA=/var/task/share/gdal \
		--env PYTHONWARNINGS=ignore \
		--env GDAL_CACHEMAX=75% \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--env CPL_TMPDIR="/tmp" \
		--env GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES \
		--env GDAL_HTTP_MULTIPLEX=YES \
		--env GDAL_HTTP_VERSION=2 \
		--env TOKEN="yo" \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env CPL_VSIL_CURL_ALLOWED_EXTENSIONS=".TIF,.ovr,.jp2,.tif" \
		-itd \
		lambci/lambda:build-python3.6 bash
	docker exec -it lambda bash -c 'unzip -q /local/package.zip -d /var/task/'
	docker exec -it lambda bash -c '/tmp/bin/tests.sh'
	docker stop lambda
	docker rm lambda

STAGENAME=production
deploy:
	cd services/cogeo && sls deploy --stage ${STAGENAME}
	cd services/landsat && sls deploy --stage ${STAGENAME}
	cd services/cbers && sls deploy --stage ${STAGENAME}
	#cd services/sentinel && sls deploy --stage ${STAGENAME}

clean:
	docker stop lambda
	docker rm lambda
