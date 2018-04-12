#!/bin/env python

import os, sys, sqlite3, re, json, optparse

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

opt_parser = optparse.OptionParser()
opt_parser.add_option('-g', '--geom_column', dest='geom_column', action='store', default='boundary', help='Column to index for boundary_geom (values: boundary or boundary_simple).')
opt_parser.add_option('-m', '--min_session', dest='min_session', action='store', type='int', default=0, help='Minimum congressional session to index (values: 0-115).')
options, args = opt_parser.parse_args()

db_url = os.getenv('DATABASE_URL', 'sqlite://%s/us_congress.db' % root_dir)

if db_url:
	print("Indexing to %s"  % db_url)
	print("with options:")
	print("  geom_column = %s" % options.geom_column)
	print("  min_session = %d" % options.min_session)
else:
	print("No DATABASE_URL environment variable set.\nexport DATABASE_URL='sqlite://us-congress.db'")
	sys.exit(1)

sqlite = re.search('^sqlite://(.+)$', db_url)

if sqlite:
	db_filename = '%s/%s' % (root_dir, sqlite.group(1))

else:
	print("Could not parse DATABASE_URL.")
	sys.exit(1)

if os.path.exists(db_filename):
	print("%s exists, bailing out." % db_filename)
	sys.exit(1)

conn = sqlite3.connect(db_filename)
cur = conn.cursor()

cur.execute('''
CREATE TABLE districts (
	id TEXT PRIMARY KEY,
	state TEXT,
	start_session INTEGER,
	end_session INTEGER,
	district_num TEXT,
	boundary TEXT,
	boundary_simple TEXT
)''')

conn.commit()

for state in os.listdir("data"):

	if state.startswith("."):
		continue

	cur = conn.cursor()
	state_dir = "data/%s" % state

	state_districts = []

	for filename in os.listdir(state_dir):

		if filename.endswith('.display.geojson'):
			continue

		matches = re.search('^(\w+)_(\d+)_to_(\d+)_([0-9-]+)\.lookup\.geojson$', filename)
		if matches == None:
			print("skipping %s" % filename)
			continue

		state = matches.group(1)
		start_session = int(matches.group(2))
		end_session = int(matches.group(3))
		district_num = int(matches.group(4))

		if end_session < options.min_session:
			continue

		print(filename)

		path = "%s/%s" % (state_dir, filename)

		with open(path) as data_file:
			data = json.load(data_file)

		geometry = data["geometry"]
		boundary = json.dumps(geometry)

		simplified_path = path.replace('.lookup.geojson', '.display.geojson')
		with open(simplified_path) as data_file:
			data = json.load(data_file)

		geometry = data["geometry"]
		boundary_simplified = json.dumps(geometry)

		district = [
			filename.replace('.lookup.geojson', ''),
			state,
			start_session,
			end_session,
			district_num,
			boundary,
			boundary_simplified
		]
		state_districts.append(district)

	cur.executemany('''
		INSERT INTO districts (
			id,
			state,
			start_session,
			end_session,
			district_num,
			boundary,
			boundary_simple
		)
		VALUES (?, ?, ?, ?, ?, ?, ?)''', state_districts)
	conn.commit()

conn.close()

# see also: http://www.gaia-gis.it/spatialite-2.4.0-4/splite-python.html

from pyspatialite import dbapi2 as db

conn = db.connect(db_filename)
cur = conn.cursor()

rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
for row in rs:
    msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
    print msg

print("Initializing spatial metadata")
cur.execute("SELECT InitSpatialMetadata()")

print("Adding geometry column: districts.boundary_geom")
cur.execute("SELECT AddGeometryColumn('districts', 'boundary_geom', 4326, 'GEOMETRY', 'XY')")

print("Updating districts.boundary_geom from districts.boundary GeoJSON")
cur.execute("UPDATE districts SET boundary_geom = SetSRID(GeomFromGeoJSON(boundary), 4326)")

print("Creating spatial index")
cur.execute("SELECT CreateSpatialIndex('districts', 'boundary_geom')")

print("Committing queries")
conn.commit()

print("Done")
conn.close()
