#!/bin/bash

WHOAMI=`python -c 'import os, sys; print os.path.realpath(sys.argv[1])' $0`
SCRIPTS=`dirname $WHOAMI`
ROOT=`dirname $SCRIPTS`

for file in "$ROOT/data/*/*.geojson"; do \
	simple=`echo $file | sed -e "s/\.geojson/.dp20.geojson/"` ; \
	if [[ $simple = *".dp20.dp20"* ]] ; then \
		if [ -f "$simple" ] ; then
			echo "Removing $simple" ; \
			rm $simple ; \
		fi \
	else \
		echo $simple ; \
		if [ ! -f "$simple" ] ; then \
			mapshaper $file \
				-simplify dp 20% \
				-o format=geojson geojson-type=Feature \
				$simple ; \
		fi \
	fi \
done
