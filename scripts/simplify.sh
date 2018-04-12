#!/bin/bash

WHOAMI=`python -c 'import os, sys; print os.path.realpath(sys.argv[1])' $0`
SCRIPTS=`dirname $WHOAMI`
ROOT=`dirname $SCRIPTS`

for file in $ROOT/data/*/*.lookup.geojson ; do \
	simple=`echo $file | sed -e "s/\.lookup\.geojson/.display.geojson/"` ; \
	echo $simple ; \
	if [ ! -f "$simple" ] ; then \
		mapshaper $file \
			-simplify visvalingam interval=100 \
			-o format=geojson geojson-type=Feature \
			$simple ; \
	fi \
done
