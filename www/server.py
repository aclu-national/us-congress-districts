#!/usr/bin/env python

import flask, flask_cors, json, os, psycopg2, re, sys
from pyspatialite import dbapi2

app = flask.Flask(__name__)
flask_cors.CORS(app)

@app.before_request
def init():

	print("init")
	db_url = os.getenv('DATABASE_URL')

	if not db_url:
		print("No DATABASE_URL environment variable set.")
		sys.exit(1)

	postgres = re.search('^postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)$', db_url)
	sqlite = re.search('^sqlite://(.+)$', db_url)

	if postgres:
		db_vars = (
		    postgres.group(5), # dbname
		    postgres.group(3), # host
		    postgres.group(4), # port
		    postgres.group(1), # user
		    postgres.group(2)  # password
		)
		db_dsn = "dbname=%s host=%s port=%s user=%s password=%s" % db_vars
		flask.g.db_type = "postgres"
		flask.g.db = psycopg2.connect(db_dsn)

	elif sqlite:
		db_dsn = sqlite.group(1)
		flask.g.db_type = "sqlite"
		flask.g.db = dbapi2.connect(db_dsn)
		flask.g.db.row_factory = dbapi2.Row

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

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include lat and lng args."

	if flask.g.db_type == "sqlite":
		return pip_sqlite(lat, lng)
	if flask.g.db_type == "postgis":
		return pip_postgres(lat, lng)
	else:
		return "No database configured."

def pip_sqlite(lat, lng):

	cur = flask.g.db.cursor()
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

def pip_postgres(lat, lng):

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
