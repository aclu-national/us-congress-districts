#!/bin/bash

WHOAMI=`python -c 'import os, sys; print os.path.realpath(sys.argv[1])' $0`
SCRIPTS=`dirname $WHOAMI`
ROOT=`dirname $SCRIPTS`

for file in $ROOT/data/*/*.geojson ; do \
	new_file=`echo $file | sed -e "s/0\([0-9]\)\.geojson/\1.lookup.geojson/"` ; \
	new_file=`echo $new_file | sed -e "s/0\([0-9]\)\.dp20\.geojson/\1.dp20.geojson/"` ; \
	new_file=`echo $new_file | sed -e "s/\.dp20\.geojson/.display.geojson/"` ; \
	if [[ $new_file != $file ]] ; then \
		#echo "$file => $new_file" ; \
		git mv $file $new_file ; \
	fi \
done
