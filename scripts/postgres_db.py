#!/bin/env python

import os, psycopg2, re, sys

def connect():

	db_url = os.getenv('DATABASE_URL')
	if db_url:
		print("Indexing to %s"  % db_url)
	else:
		print("No DATABASE_URL environment variable set.\nexport DATABASE_URL='postgres://user:pass@host/dbname'")
		sys.exit(1)

	postgres = re.search('^postgres://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)$', db_url)
	postgres_dbname = re.search('^postgres://(\w+)$', db_url)

	if postgres:
		db_vars = (
			postgres.group(5), # dbname
			postgres.group(3), # host
			postgres.group(4), # port
			postgres.group(1), # user
			postgres.group(2)  # password
		)
		db_dsn = "dbname=%s host=%s port=%s user=%s password=%s" % db_vars

	elif postgres_dbname:
		db_dsn = "dbname=%s" % postgres_dbname.group(1)

	else:
		print("Could not parse DATABASE_URL. Note: this one only works on PostGIS.")
		sys.exit(1)

	conn = psycopg2.connect(db_dsn)
	return conn
