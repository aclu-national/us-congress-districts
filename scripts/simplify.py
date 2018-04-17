#!/bin/env python

import os, sys, re, json

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

#min_interval = 10.0
#max_interval = 100.0
#min_area = 1225433.0
#max_area = 1716598874914.0
#area_range = max_area - min_area

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
		path = "%s/%s" % (state_dir, filename)
		simple_path = path.replace('.lookup.geojson', '.display.geojson')

		# HEY, a quick thing about these mapshaper arguments: they need to be
		# updated in more than one place. The 'simplify' args should be kept in
		# sync with the ones in save_113_display.py. (20180417/dphiffer)
		simplify = "-filter-islands min-area=500000 -simplify resolution=300"
		output = "-o format=geojson geojson-type=Feature"
		cmd = "mapshaper %s %s %s %s" % (path, simplify, output, simple_path)
		os.system(cmd)
