#!/bin/env python

import os, sys, sqlite3, re, json

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

filename = '%s/us-congress.db' % root_dir

if os.path.exists(filename):
    print("%s exists, bailing out." % filename)
    sys.exit(1)

conn = sqlite3.connect(filename)
cur = conn.cursor()

cur.execute('''CREATE TABLE districts (
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

        if filename.endswith('.dp20.geojson'):
            continue

        matches = re.search('^(\w+)_(\d+)_to_(\d+)_([0-9-]+)\.geojson$', filename)
        if matches == None:
            print("skipping %s" % filename)
            continue

        print(filename)
        path = "%s/%s" % (state_dir, filename)

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
            matches.group(1),
            int(matches.group(2)),
            int(matches.group(3)),
            matches.group(4),
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

conn = db.connect(filename)
cur = conn.cursor()

rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
for row in rs:
    msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
    print msg

print("Initializing spatial metadata")
cur.execute("SELECT InitSpatialMetadata()")

print("Adding geometry column: districts.boundary_geom")
cur.execute("SELECT AddGeometryColumn('districts', 'boundary_geom', 3857, 'GEOMETRY')")

print("Updating districts.boundary_geom from districts.boundary GeoJSON")
cur.execute("UPDATE districts SET boundary_geom = SetSRID(GeomFromGeoJSON(boundary), 3857)")

print("Creating spatial index")
cur.execute("SELECT CreateSpatialIndex('districts', 'boundary_geom')")

print("Committing queries")
conn.commit()

print("Done")
conn.close()
