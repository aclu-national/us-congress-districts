#!/usr/bin/env python

import flask, flask_cors, json, psycopg2
from pyspatialite import dbapi2

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.before_request
def init():
	flask.g.spatialite = dbapi2.connect('../us-congress.db')
	flask.g.spatialite.row_factory = dbapi2.Row
	flask.g.postgis = psycopg2.connect("dbname=us_congress")
	flask.g.pip_provider = "postgis"

@app.route("/")
def map():
	return flask.render_template('map.html')

@app.route('/assets/<path:path>')
def assets(path):
	return flask.send_from_directory('assets', path)

@app.route('/data/<path:path>')
def data(path):
	return flask.send_from_directory('../data', path)

@app.route("/pip")
def pip():
	if flask.g.pip_provider == "spatialite":
		return spatialite()
	elif flask.g.pip_provider == "postgis":
		return postgis()
	else:
		return "No PIP provider configured."

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
