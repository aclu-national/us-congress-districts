#!/usr/bin/env python

import flask, json
from pyspatialite import dbapi2 as db

app = flask.Flask(__name__)

@app.before_request
def init():
	flask.g.conn = db.connect('us-congress.db')
	flask.g.conn.row_factory = db.Row

@app.route("/")
def hello():
	return "Hi, you probably want to try /pip instead."

@app.route("/pip")
def pip():

	lat = flask.request.args.get('lat', None)
	lng = flask.request.args.get('lng', None)

	if lat == None or lng == None:
		return "Please include lat and lng args."

	cur = flask.g.conn.cursor()
	rs = cur.execute("SELECT id, boundary_simple FROM districts WHERE within(GeomFromText('POINT({lng} {lat})'), boundary_geom) AND rowid IN (SELECT pkid FROM idx_districts_boundary_geom WHERE xmin < {lng} AND xmax > {lng} AND ymin < {lat} AND ymax > {lat}) ORDER BY end_session DESC".format(lat=lat, lng=lng))

	results = []
	for row in rs:
		results.append({
			'id': row[0],
			'geom': row[1]
		})

	cur.close()

	rsp = {
		'ok': 1,
		'results': results
	}
	return flask.jsonify(rsp)

if __name__ == '__main__':
	app.run(debug=True)
