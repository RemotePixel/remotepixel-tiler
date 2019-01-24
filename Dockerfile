FROM remotepixel/amazonlinux-gdal:2.4.0

WORKDIR /tmp

ENV PACKAGE_PREFIX /tmp/python

COPY setup.py setup.py
COPY remotepixel_tiler/ remotepixel_tiler/

# Install dependencies
RUN pip3 install . --no-binary numpy,rasterio -t $PACKAGE_PREFIX -U

################################################################################
#                            REDUCE PACKAGE SIZE                               #
################################################################################

RUN find $PACKAGE_PREFIX -name "*-info" -type d -exec rm -rdf {} +
RUN rm -rdf $PACKAGE_PREFIX/boto3/ \
  && rm -rdf $PACKAGE_PREFIX/botocore/ \
  && rm -rdf $PACKAGE_PREFIX/docutils/ \
  && rm -rdf $PACKAGE_PREFIX/dateutil/ \
  && rm -rdf $PACKAGE_PREFIX/jmespath/ \
  && rm -rdf $PACKAGE_PREFIX/s3transfer/ \
  && rm -rdf $PACKAGE_PREFIX/numpy/doc/

# Leave module precompiles for faster Lambda startup
RUN find $PACKAGE_PREFIX -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-36//'); cp $f $n; done;
RUN find $PACKAGE_PREFIX -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
RUN find $PACKAGE_PREFIX -type f -a -name '*.py' -print0 | xargs -0 rm -f

RUN cd $PREFIX && find lib -name \*.so\* -exec strip {} \;
RUN cd $PREFIX && find lib64 -name \*.so\* -exec strip {} \;

################################################################################
#                              CREATE ARCHIVE                                  #
################################################################################

RUN cd $PACKAGE_PREFIX && zip -r9q /tmp/package.zip *
RUN cd $PREFIX && zip -r9q --symlinks /tmp/package.zip lib/*.so*
RUN cd $PREFIX && zip -r9q --symlinks /tmp/package.zip lib64/*.so*
RUN cd $PREFIX && zip -r9q /tmp/package.zip share
