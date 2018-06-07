#!/bin/env python

import os, sys, psycopg2, re, json, optparse
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

opt_parser = optparse.OptionParser()
opt_parser.add_option('-g', '--geom_column', dest='geom_column', action='store', default='boundary', help='Column to index for boundary_geom (values: boundary or boundary_simple).')
opt_parser.add_option('-m', '--min_session', dest='min_session', action='store', type='int', default=0, help='Minimum congressional session to index (values: 0-115).')
options, args = opt_parser.parse_args()

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS districts CASCADE")
cur.execute('''
	CREATE TABLE districts (
		id INTEGER PRIMARY KEY,
		name VARCHAR(255),
		state CHAR(2),
		start_session INTEGER,
		end_session INTEGER,
		district_num INTEGER,
		at_large_only CHAR DEFAULT 'N',
		boundary TEXT,
		boundary_simple TEXT,
		boundary_geom GEOMETRY,
		area FLOAT
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO districts (
		id,
		name,
		state,
		start_session,
		end_session,
		district_num,
		boundary,
		boundary_simple,
		area
	) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

states = []
for state in os.listdir("data"):

	if not re.match("^\w\w$", state):
		continue

	states.append(state)

states.sort()

for state in states:

	cur = conn.cursor()
	state_dir = "%s/data/%s" % (root_dir, state)

	state_records = []

	files = []
	for filename in os.listdir(state_dir):
		if not filename.endswith(".lookup.geojson"):
			continue
		files.append(filename)

	files.sort()
	for filename in files:

		regex = '^(\w+)_(\d+)_to_(\d+)_([0-9-]+)\.lookup\.geojson$'
		matches = re.search(regex, filename)
		if matches == None:
			print("skipping %s" % filename)
			continue

		path = "%s/%s" % (state_dir, filename)
		name = filename.replace('.lookup.geojson', '')
		state = matches.group(1)
		start_session = int(matches.group(2))
		end_session = int(matches.group(3))
		district_num = int(matches.group(4))

		if end_session < options.min_session:
			continue

		print(filename)

		with open(path) as geojson:
			feature = json.load(geojson)

		geometry = feature["geometry"]
		boundary = json.dumps(geometry)
		area = float(feature["properties"]["area"])

		simplified_path = path.replace('.lookup.geojson', '.display.geojson')
		with open(simplified_path) as simplified_geojson:
			simplified_feature = json.load(simplified_geojson)

		geometry = simplified_feature["geometry"]
		boundary_simplified = json.dumps(geometry)

		id = int(feature["properties"]["aclu_id"].split(":")[1])

		district = [
			id,
			name,
			state,
			start_session,
			end_session,
			district_num,
			boundary,
			boundary_simplified,
			area
		]
		cur.execute(insert_sql, district)

	conn.commit()

print("Marking excess at-large districts")
cur.execute('''
	UPDATE districts
	SET at_large_only = 'Y'
	WHERE district_num = 0 AND (
		SELECT count(id)
		FROM districts AS d
		WHERE d.start_session <= districts.end_session
		  AND d.end_session >= districts.start_session
		  AND d.state = districts.state
	) = 1
''')

print("Indexing postgis geometry")
cur.execute('''
	UPDATE districts
	SET boundary_geom = ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326)
''' % options.geom_column)
cur.execute('''
	CREATE INDEX districts_boundary_gix ON districts USING GIST (boundary_geom)
''')
conn.commit()

conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
cur.execute('''
	VACUUM ANALYZE districts
''')

conn.close()
print("Done")
