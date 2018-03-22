#!/bin/env python

# see also: http://www.gaia-gis.it/spatialite-2.4.0-4/splite-python.html

from pyspatialite import dbapi2 as db

conn = db.connect('us-congress.db')
cur = conn.cursor()

rs = cur.execute('SELECT sqlite_version(), spatialite_version()')
for row in rs:
    msg = "> SQLite v%s Spatialite v%s" % (row[0], row[1])
    print msg

print("Initializing spatial metadata")
cur.execute("SELECT InitSpatialMetadata()")

print("Adding geometry column: us_congress.boundary_geom")
cur.execute("SELECT AddGeometryColumn('us_congress', 'boundary_geom', 3857, 'MULTIPOLYGON')")

print("Updating us_congress.boundary_geom from us_congress.boundary GeoJSON")
cur.execute("UPDATE us_congress SET boundary_geom = SetSRID(GeomFromGeoJSON(boundary), 3857)")

print("Creating spatial index")
cur.execute("SELECT CreateSpatialIndex('us_congress', 'boundary_geom')")

print("Committing queries")
conn.commit()

print("Done")
conn.close()
