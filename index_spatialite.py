#!/bin/env python

import os, sys, sqlite3, re, json

filename = 'us-congress.db'

if os.path.exists(filename):
    print("%s exists, bailing out." % filename)
    sys.exit(1)

conn = sqlite3.connect(filename)
cur = conn.cursor()

cur.execute('''CREATE TABLE us_congress (
               id TEXT PRIMARY KEY,
               state TEXT,
               start_session INTEGER,
               end_session INTEGER,
               boundary TEXT,
               boundary_simple TEXT
             )''')

conn.commit()

for state in os.listdir("data"):

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

        record = [
            filename.replace('.geojson', ''),
            matches.group(1),
            int(matches.group(2)),
            int(matches.group(3)),
            boundary,
            boundary_simplified
        ]
        state_records.append(record)

    cur.executemany('INSERT INTO us_congress VALUES (?, ?, ?, ?, ?, ?)', state_records)
    conn.commit()

conn.close()
