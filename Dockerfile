FROM remotepixel/amazonlinux-gdal:2.4.2

# Install dependencies
RUN pip3 install pip -U
RUN pip3 install cython==0.28

ENV PACKAGE_TMP /tmp/package

COPY setup.py setup.py
COPY remotepixel_tiler/ remotepixel_tiler/

RUN pip3 install . --no-binary numpy,rasterio -t $PACKAGE_TMP -U
