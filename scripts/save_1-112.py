#!/bin/env python

import json, os, sys, re
import us
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils

script = os.path.realpath(sys.argv[1])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)
dirname = "%s/congressional-district-boundaries-master" % root_dir

for filename in os.listdir(dirname):

	if not filename.endswith(".geojson"):
		continue

	matches = re.search('^(\w+)_(\d+)_to_(\d+)\.geojson$', filename)

	state_name = matches.group(1)
	if (state_name == 'District_Of_Columbia'):
		state = 'dc'
	else:
		state_name = unicode(state_name.replace('_', ' '))
		state = us.states.lookup(state_name).abbr
		state = str(state.lower())
	start = int(matches.group(2))
	end = int(matches.group(3))

	print("Loading %s" % filename)
	with open(dirname + "/" + filename) as data_file:
		data = json.load(data_file)

	for feature in data["features"]:

		props = feature["properties"]
		district = int(props["district"])
		if district < 10 and district != -1:
			district = "0%d" % district
		else:
			district = "%d" % district

		path = "data/%s/%s_%d_to_%d_%s.geojson" % (state, state, start, end, district)
		print "Saving %s" % path

		feature["id"] = "%s_%d_to_%d_%s" % (state, start, end, district)
		mapzen.whosonfirst.utils.ensure_bbox(feature)

		statedir = os.path.dirname(path)
		if not os.path.exists(statedir):
			os.makedirs(statedir)

		with open(path, 'w') as outfile:
			encoder.encode_feature(feature, outfile)
