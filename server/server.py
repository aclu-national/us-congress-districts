#!/usr/bin/env python

import flask, flask_cors, json, os, psycopg2, re, sys

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.before_request
def init():
	db_connect()

def db_connect():
	default_dsn = "user=postgres password=%s" % os.getenv('POSTGRES_PASSWORD')
	db_dsn = os.getenv('POSTGRES_DSN', default_dsn)
	flask.g.db = psycopg2.connect(db_dsn)

@app.route("/")
def hello():
	return "Hello, you probably want to use: /pip"

@app.route("/pip")
def pip():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include lat and lng args."

	cur = flask.g.db.cursor()
	cur.execute('''
		SELECT id, start_session, end_session, district_num, boundary_simple
		FROM districts
		WHERE ST_within(ST_GeomFromText('POINT({lng} {lat})', 4326), boundary_geom)
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
	app.run(port=5000)
