#!/bin/bash

for file in data/*/*.geojson; do \
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
