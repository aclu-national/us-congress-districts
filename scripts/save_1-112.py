#!/bin/env python

import json, os, sys, re
import us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)
dirname = "%s/sources/1-112" % root_dir

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("SELECT id, start_date, end_date FROM sessions")
rs = cur.fetchall()
sessions = {}
if rs:
	for row in rs:
		id = row[0]
		sessions[id] = {
			"start_date": str(row[1]),
			"end_date": str(row[2])
		}

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

		path = "data/%s/%s_%d_to_%d_%s.lookup.geojson" % (state, state, start, end, district)
		print "Saving %s" % path

		feature["id"] = "%s_%d_to_%d_%s" % (state, start, end, district)
		feature["properties"] = {
			"state": state,
			"start_session": start,
			"start_date": sessions[start]["start_date"],
			"end_session": end,
			"end_date": sessions[end]["end_date"],
			"district": district
		}
		mapzen.whosonfirst.utils.ensure_bbox(feature)
		feature["properties"]["area"] = area.area(feature["geometry"])

		statedir = os.path.dirname(path)
		if not os.path.exists(statedir):
			os.makedirs(statedir)

		with open(path, 'w') as outfile:
			encoder.encode_feature(feature, outfile)
