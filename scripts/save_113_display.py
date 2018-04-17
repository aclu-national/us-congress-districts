#!/bin/env python

import json, os, sys
import us, area
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

path = "%s/cb_2013_us_cd113_5m.geojson" % root_dir

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

print("Loading cb_2013_us_cd113_5m.geojson")
with open(path) as data_file:
	data = json.load(data_file)

for feature in data["features"]:

	props = feature["properties"]
	state_fips = props["STATEFP"]
	state = us.states.lookup(state_fips).abbr
	state = str(state).lower()

	if props["CD113FP"] == "ZZ":
		print("skipping %s_113_to_115_ZZ" % state)
		continue

	district = int(props["CD113FP"])

	path = "%s/data/%s/%s_113_to_115_%s.display.geojson" % (root_dir, state, state, district)
	print "Saving %s" % path
	feature["properties"] = {
		"state": state,
		"start_session": 113,
		"start_date": sessions[113]["start_date"],
		"end_session": 115,
		"end_date": sessions[115]["end_date"],
		"district": district
	}
	feature["id"] = "%s_113_to_115_%s" % (state, district)

	mapzen.whosonfirst.utils.ensure_bbox(feature)
	feature["properties"]["area"] = area.area(feature["geometry"])

	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		os.makedirs(dirname)

	with open(path, 'w') as outfile:
		json.dump(feature, outfile)

	# HEY, a quick thing about these mapshaper arguments: they need to be
	# updated in more than one place. The 'simplify' args should be kept in
	# sync with the ones in simplify.py. The 'output' args here have one
	# additional 'force' argument, since we need to update the geometries
	# in place. (20180417/dphiffer)
	simplify = "-filter-islands min-area=500000 -simplify resolution=300"
	output = "-o format=geojson geojson-type=Feature force"
	cmd = "mapshaper %s %s %s %s" % (path, simplify, output, path)
	os.system(cmd)
