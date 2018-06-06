#!/bin/env python

import os, sys, psycopg2, re, json
import mapzen.whosonfirst.geojson
import mapzen.whosonfirst.utils
import data_index

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

encoder = mapzen.whosonfirst.geojson.encoder(precision=None)

states = []
for state in os.listdir("data"):

	if state.startswith("."):
		continue

	states.append(state)

states.sort()

for state in states:

	state_dir = "%s/data/%s" % (root_dir, state)

	state_records = []

	files = []
	for filename in os.listdir(state_dir):
		if not filename.endswith(".lookup.geojson"):
			continue
		files.append(filename)

	files.sort()
	for filename in files:

		path = "%s/%s" % (state, filename)
		abs_path = "%s/data/%s" % (root_dir, path)

		with open(abs_path) as json_file:
			feature = json.load(json_file)

		props = feature["properties"]
		district = props["district"]
		state = props["state"]
		start = props["start_session"]
		end = props["end_session"]

		name = "%s %s to %s %d" % (state, start, end, district)
		aclu_id = data_index.get_id('us-congress-districts', 'district', path, name)
		ocd_id = 'ocd-division/country:us/state:%s/cd:%s' % (state, district)

		feature["id"] = aclu_id
		feature["properties"]["aclu_id"] = aclu_id
		feature["properties"]["ocd_id"] = ocd_id

		print(filename)
		with open(abs_path, 'w') as outfile:
			encoder.encode_feature(feature, outfile)

		display = abs_path.replace('lookup', 'display')
		with open(display) as json_file:
			feature = json.load(json_file)

		feature["id"] = aclu_id
		feature["properties"]["aclu_id"] = aclu_id
		feature["properties"]["ocd_id"] = ocd_id

		with open(display, 'w') as outfile:
			json.dump(feature, outfile)

print('Saving index')
data_index.save_index('us-congress-districts')
