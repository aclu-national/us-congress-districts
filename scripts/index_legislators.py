#!/bin/env python

import psycopg2, os, re, sys, yaml, json
import postgres_db

script = os.path.realpath(sys.argv[0])
scripts_dir = os.path.dirname(script)
root_dir = os.path.dirname(scripts_dir)

conn = postgres_db.connect()
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS legislators CASCADE")
cur.execute('''
	CREATE TABLE legislators (
		id SERIAL PRIMARY KEY,
		first_name VARCHAR(255),
		last_name VARCHAR(255),
		full_name VARCHAR(255),
		birthday DATE,
		gender VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_concordances CASCADE")
cur.execute('''
	CREATE TABLE legislator_concordances (
		legislator_id INTEGER,
		concordance_name VARCHAR(255),
		concordance_value VARCHAR(255)
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_terms CASCADE")
cur.execute('''
	CREATE TABLE legislator_terms (
		id SERIAL PRIMARY KEY,
		legislator_id INTEGER,
		type VARCHAR(16),
		state CHAR(2),
		district INTEGER,
		start_date DATE,
		end_date DATE,
		party VARCHAR(32)
	)
''')
cur.execute('''
	CREATE INDEX legislator_term_lookup_idx ON legislator_terms (
		state,
		district,
		start_date
	)
''')

cur.execute("DROP TABLE IF EXISTS legislator_term_details CASCADE")
cur.execute('''
	CREATE TABLE legislator_term_details (
		term_id INTEGER,
		legislator_id INTEGER,
		detail_name VARCHAR(255),
		detail_value VARCHAR(255)
	)
''')

conn.commit()

def index_legislators(conn, file):

	cur = conn.cursor()

	print("Loading %s" % file)
	file = open(file, "r")
	data = yaml.load(file)

	legislator_insert_sql = '''
		INSERT INTO legislators (
			first_name,
			last_name,
			full_name
		) VALUES (%s, %s, %s) RETURNING id
	'''

	concordances_insert_sql = '''
		INSERT INTO legislator_concordances (
			legislator_id,
			concordance_name,
			concordance_value
		) VALUES (%s, %s, %s)
	'''

	terms_insert_sql = '''
		INSERT INTO legislator_terms (
			{columns}
		) VALUES ({placeholders}) RETURNING id
	'''

	details_insert_sql = '''
		INSERT INTO legislator_term_details (
			term_id,
			legislator_id,
			detail_name,
			detail_value
		) VALUES (%s, %s, %s, %s)
	'''

	term_keys = ["type", "state", "district", "start", "end", "party"]

	for legislator in data:

		values = [
			legislator["name"]["first"],
			legislator["name"]["last"]
		]

		if "official_full" in legislator["name"]:
			values.append(legislator["name"]["official_full"])
		else:
			full_name = "%s %s" % (
				legislator["name"]["first"],
				legislator["name"]["last"]
			)
			values.append(full_name)

		values = tuple(values)
		cur.execute(legislator_insert_sql, values)
		id = cur.fetchone()[0]
		print("%d. %s" % (id, values[2]))

		if "bio" in legislator and "birthday" in legislator["bio"]:
			cur.execute('''
				UPDATE legislators
				SET birthday = %s
				WHERE id = %s
			''', (legislator["bio"]["birthday"], id))

		if "bio" in legislator and "gender" in legislator["bio"]:
			cur.execute('''
				UPDATE legislators
				SET gender = %s
				WHERE id = %s
			''', (legislator["bio"]["gender"], id))

		for key, value in legislator["id"].iteritems():

			if isinstance(value, list):
				value = ",".join(value)

			values = (
				id,
				key,
				value
			)
			cur.execute(concordances_insert_sql, values)
			#print("\t%s = %s" % (key, value))

		for term in legislator["terms"]:

			columns = ["legislator_id"]
			values = [id]
			placeholders = ["%s"]
			details = []

			for key, value in term.iteritems():
				if key in term_keys:

					if key == "start" or key == "end":
						key = "%s_date" % key
					elif key == "state":
						value = value.lower()

					columns.append(key)
					values.append(value)
					placeholders.append("%s")

					#print("\t%s = %s" % (key, value))
				else:
					if isinstance(value, list) or isinstance(value, dict):
						value = json.dumps(value)
					#print("\t%s = %s (detail)" % (key, value))
					details.append([key, value])

			columns = ", ".join(columns)
			placeholders = ", ".join(placeholders)
			values = tuple(values)

			sql = terms_insert_sql.format(columns=columns, placeholders=placeholders)

			cur.execute(sql, values)
			term_id = cur.fetchone()[0]

			for detail in details:
				values = [id, term_id] + detail
				cur.execute(details_insert_sql, values)

		conn.commit()

index_legislators(conn, "%s/sources/legislators/current.yaml" % root_dir)
index_legislators(conn, "%s/sources/legislators/historical.yaml" % root_dir)

conn.close()
print("done")
