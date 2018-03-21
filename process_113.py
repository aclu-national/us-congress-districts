#!/bin/env python

import json, os
import us
import mapzen.whosonfirst.geojson

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading tl_rd13_us_cd113.geojson")
with open("tl_rd13_us_cd113.geojson") as data_file:
	data = json.load(data_file)

for feature in data["features"]:
	dir(feature)
	props = feature["properties"]
	state_fips = props["STATEFP"]
	state = us.states.lookup(state_fips).abbr
	state = str(state).lower()
	code = props["CD113FP"]
	path = "113/113-%s-%s.geojson" % (state, code)

	print "Saving %s" % path

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)
