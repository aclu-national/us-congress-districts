#!/bin/env python

import os, sys, re, json

def simplify(path):
	output_path = path.replace('.lookup.geojson', '.display.geojson')
	simplify_args = "-filter-islands min-area=500000 -simplify resolution=300"
	output_args = "-o format=geojson geojson-type=Feature force"
	cmd = "mapshaper %s %s %s %s" % (path, simplify_args, output_args, output_path)
	os.system(cmd)

if __name__ == "__main__":
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
			simplify(path)
