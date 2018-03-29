#!/bin/env python

import os, sys, psycopg2, re, json

min_session_num = 66

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

db_url = os.getenv('DATABASE_URL')

if not db_url:
	print("No DATABASE_URL environment variable set.")
	sys.exit(1)

postgres = re.search('^postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)$', db_url)
postgres_dbname = re.search('^postgres://(\w+)$', db_url)

if postgres:
	db_vars = (
		postgres.group(5), # dbname
		postgres.group(3), # host
		postgres.group(4), # port
		postgres.group(1), # user
		postgres.group(2)  # password
	)
	db_dsn = "dbname=%s host=%s port=%s user=%s password=%s" % db_vars

elif postgres_dbname:
	db_dsn = "dbname=%s" % postgres_dbname.group(1)

else:
	print("Could not parse DATABASE_URL.")
	sys.exit(1)

conn = psycopg2.connect(db_dsn)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS districts")
cur.execute('''
	CREATE TABLE districts (
		id VARCHAR(255) PRIMARY KEY,
		state CHAR(2),
		start_session INTEGER,
		end_session INTEGER,
		district_num INTEGER,
		boundary TEXT,
		boundary_simple TEXT,
		boundary_geom GEOMETRY
	)''')
conn.commit()

insert_sql = '''
	INSERT INTO districts (
		id,
		state,
		start_session,
		end_session,
		district_num,
		boundary,
		boundary_simple
	) VALUES (%s, %s, %s, %s, %s, %s, %s)
'''

for state in os.listdir("data"):

	if state.startswith("."):
		continue

	cur = conn.cursor()
	state_dir = "%s/data/%s" % (root_dir, state)

	state_records = []

	for filename in os.listdir(state_dir):

		if filename.endswith(".dp20.geojson"):
			continue

		path = "%s/%s" % (state_dir, filename)

		matches = re.search('^(\w+)_(\d+)_to_(\d+)_([0-9-]+)\.geojson$', filename)
		if matches == None:
			print("skipping %s" % filename)
			continue

		state = matches.group(1)
		start_session = int(matches.group(2))
		end_session = int(matches.group(2))
		district_num = int(matches.group(4))

		if min_session_num and end_session < min_session_num:
			continue

		print(filename)

		with open(path) as data_file:
			data = json.load(data_file)

		geometry = data["geometry"]
		boundary = json.dumps(geometry)

		simplified_path = path.replace('.geojson', '.dp20.geojson')
		with open(simplified_path) as data_file:
			data = json.load(data_file)

		geometry = data["geometry"]
		boundary_simplified = json.dumps(geometry)

		district = [
			filename.replace('.geojson', ''),
			state,
			start_session,
			end_session,
			district_num,
			boundary,
			boundary_simplified
		]
		cur.execute(insert_sql, district)

	conn.commit()

print("Indexing postgis geometry")
cur.execute('''
	UPDATE districts
	SET boundary_geom = ST_SetSRID(ST_GeomFromGeoJSON(boundary), 3857)
''')
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
