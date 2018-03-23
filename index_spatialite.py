#!/bin/env python

import os, sys, sqlite3, re, json

filename = 'us-congress.db'

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
