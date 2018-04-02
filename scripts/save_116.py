#!/bin/env python

import json, os, sys
import us
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/pa_116.geojson" % root_dir

conn = postgres_db.connect()
cur = conn.cursor()

sessions = {}
sessions[116] = {
	"start_date": "2019-01-03",
	"end_date": "2021-01-03"
}

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

print("Loading pa_116.geojson")
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state = "pa"

	district = int(props["DISTRICT"])

	path = "%s/data/pa/pa_116_to_116_%s.lookup.geojson" % (root_dir, district)
	print "Saving %s" % path
	feature["properties"] = {
		"state": state,
		"start_session": 116,
		"start_date": sessions[116]["start_date"],
		"end_session": 116,
		"end_date": sessions[116]["end_date"],
		"district": district
	}
	feature["id"] = "pa_116_to_116_%s" % district

	mapzen.whosonfirst.utils.ensure_bbox(feature)

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		encoder.encode_feature(feature, outfile)
