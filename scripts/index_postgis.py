#!/bin/env python

import os, sys, psycopg2, re, json, optparse

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

opt_parser = optparse.OptionParser()
opt_parser.add_option('-g', '--geom_column', dest='geom_column', action='store', default='boundary', help='Column to index for boundary_geom (values: boundary or boundary_simple).')
opt_parser.add_option('-m', '--min_session', dest='min_session', action='store', type='int', default=0, help='Minimum congressional session to index (values: 0-115).')
options, args = opt_parser.parse_args()

db_url = os.getenv('DATABASE_URL')
if db_url:
	print("Indexing to %s"  % db_url)
	print("with options:")
	print("  geom_column = %s" % options.geom_column)
	print("  min_session = %d" % options.min_session)
else:
	print("No DATABASE_URL environment variable set.\nexport DATABASE_URL='postgres://user:pass@host/dbname'")
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

cur.execute("DROP TABLE IF EXISTS districts CASCADE")
cur.execute('''
	CREATE TABLE districts (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255),
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
		name,
		state,
		start_session,
		end_session,
		district_num,
		boundary,
		boundary_simple
	) VALUES (%s, %s, %s, %s, %s, %s, %s)
'''

states = []
for state in os.listdir("data"):

	if state.startswith("."):
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

		path = "%s/%s" % (state_dir, filename)

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
		cur.execute(insert_sql, district)

	conn.commit()

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
