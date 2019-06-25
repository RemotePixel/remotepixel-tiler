FROM remotepixel/amazonlinux-gdal:2.4.1

ENV PACKAGE_TMP /tmp/package

COPY setup.py setup.py
COPY remotepixel_tiler/ remotepixel_tiler/

# Install dependencies
RUN pip3 install cython~=0.28
RUN pip3 install . --no-binary numpy,rasterio -t $PACKAGE_TMP -U
