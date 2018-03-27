#!/bin/env python

import json, os, sys
import us
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/tl_rd13_us_cd113.geojson" % root_dir

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading tl_rd13_us_cd113.geojson")
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state_fips = props["STATEFP"]
	state = us.states.lookup(state_fips).abbr
	state = str(state).lower()
	district = props["CD113FP"]

	path = "%s/data/%s/%s_113_to_115_%s.geojson" % (root_dir, state, state, district)
	print "Saving %s" % path

	feature["id"] = "%s_113_to_115_%s" % (state, district)
	mapzen.whosonfirst.utils.ensure_bbox(feature)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)
