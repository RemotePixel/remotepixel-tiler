FROM remotepixel/amazonlinux:gdal3.0-py3.7

WORKDIR /tmp

ENV PACKAGE_PREFIX /tmp/python

COPY setup.py setup.py
COPY remotepixel_tiler/ remotepixel_tiler/

# Install dependencies
RUN pip3 install . --no-binary numpy,rasterio -t $PACKAGE_PREFIX -U