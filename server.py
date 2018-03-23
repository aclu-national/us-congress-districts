#!/usr/bin/env python

import flask, json, psycopg2
from pyspatialite import dbapi2

app = flask.Flask(__name__)

@app.before_request
def init():
	flask.g.spatialite = dbapi2.connect('us-congress.db')
	flask.g.spatialite.row_factory = dbapi2.Row
	flask.g.postgis = psycopg2.connect("dbname=us_congress")

@app.route("/")
def hello():
	return "Hi, you probably want to try /spatialite or /postgis instead."

@app.route("/spatialite")
def spatialite():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include lat and lng args."

	cur = flask.g.spatialite.cursor()
	rs = cur.execute('''
		SELECT id, start_session, end_session, district_num, boundary_simple
		FROM districts
		WHERE within(GeomFromText('POINT({lng} {lat})'), boundary_geom)
		AND rowid IN (
			SELECT pkid
			FROM idx_districts_boundary_geom
			WHERE xmin < {lng}
			  AND xmax > {lng}
			  AND ymin < {lat}
			  AND ymax > {lat}
		)
		ORDER BY end_session DESC
	'''.format(lat=lat, lng=lng))

	results = []
	for row in rs:
		results.append({
			'id': row[0],
			'start_session': row[1],
			'end_session': row[2],
			'district_num': row[3],
			'boundary_simple': row[4]
		})

	cur.close()

	rsp = {
		'ok': 1,
		'results': results
	}
	return flask.jsonify(rsp)

@app.route("/postgis")
def postgis():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include lat and lng args."

	cur = flask.g.postgis.cursor()
	cur.execute('''
		SELECT id, start_session, end_session, district_num, boundary_simple
		FROM districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 3857), boundary_geom)
		ORDER BY end_session DESC
	'''.format(lat=lat, lng=lng))

	rs = cur.fetchall()
	results = []
	if rs:
		for row in rs:
			results.append({
				'id': row[0],
				'start_session': row[1],
				'end_session': row[2],
				'district_num': row[3],
				'boundary_simple': row[4]
			})

	cur.close()

	rsp = {
		'ok': 1,
		'results': results
	}
	return flask.jsonify(rsp)

if __name__ == '__main__':
	app.run(debug=True)
