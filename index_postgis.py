#!/bin/env python

import os, sys, psycopg2, re, json

conn = psycopg2.connect("dbname=us_congress")
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS districts")
cur.execute('''CREATE TABLE districts (
               id VARCHAR(255) PRIMARY KEY,
               state CHAR(2),
               district_num VARCHAR(4),
               start_session INTEGER,
               end_session INTEGER,
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
#for state in ["ak"]:

    if state.startswith("."):
        continue

    cur = conn.cursor()
    state_dir = "data/%s" % state

    state_records = []

    for filename in os.listdir(state_dir):

        if filename.endswith(".dp20.geojson"):
            continue

        path = "%s/%s" % (state_dir, filename)

        matches = re.search('^(\w+)_(\d+)_to_(\d+)_([0-9-]+)\.geojson$', filename)
        if matches == None:
            print("skipping %s" % filename)
            continue

        print(filename)

        with open(path) as data_file:
            data = json.load(data_file)

        geometry = data["geometry"]
        geometry["type"] = "MultiPolygon"
        boundary = json.dumps(geometry)

        simplified_path = path.replace('.geojson', '.dp20.geojson')
        with open(simplified_path) as data_file:
            data = json.load(data_file)

        geometry = data["geometry"]
        geometry["type"] = "MultiPolygon"
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
        cur.execute(insert_sql, district)

    conn.commit()

conn.close()
