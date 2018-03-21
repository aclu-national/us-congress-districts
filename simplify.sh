#!/bin/bash

for file in data/*/*.geojson; do \
	simple=`echo $file | sed -e "s/\.geojson/.dp20.geojson/"` ; \
	echo $simple ; \
	mapshaper $file -simplify dp 20% -o format=geojson $simple ; \
done
