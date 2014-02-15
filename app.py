from flask import *
from pprint import pprint as pretty

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError, RqlDriverError

import argparse
import json
import os

app = Flask(__name__)

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB_NAME = "graphbox"
rethink = r.connect("localhost", 28015).repl()

def dbSetup():
	connection = r.connect(host=RDB_HOST, port=RDB_PORT)
	try:
		r.db_create(DB_NAME).run(connection)
		r.db(DB_NAME).table_create('todos').run(connection)
		print 'Database setup completed. Now run the app without --setup.'
	except RqlRuntimeError:
		print 'App database already exists. Run the app without --setup.'
	finally:
		connection.close()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/store', methods=["POST"])
def store():
	""" """

	print "STORE"
	# print dict(request.form)
	label = request.form["label"]
	color = request.form["color"]
	shape = request.form["shape"]
	# mass = request.form["mass"] # Mass will always be 50
	# print label, color, shape, mass

	node_info = {"label": label, "color": color, "shape": shape}
	# r.db(DB_NAME).table("graph1").insert(node_info).run()
	cursor = r.db(DB_NAME).table("graph1").run()
	for d in cursor:
		pretty(d)

	return "stored successfully"

if __name__ == '__main__':
	SETUPDB = True
	if SETUPDB:
		dbSetup()
	app.run(debug=True, host="localhost", port=8000)