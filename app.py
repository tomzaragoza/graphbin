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

@app.route('/store/<graphname>', methods=["POST"])
def store(graphname):
	""" 
		Store the node into the DB. 
		Will act as a function to update the coordinates 
		of the nodes as well.
	"""

	print "Storing node to DB..."
	label = request.form["label"]
	color = request.form["color"]
	shape = request.form["shape"]
	node_name = request.form["node_name"]
	x = request.form["x"]
	y = request.form["y"]

	node_info = {
					"label": label,
					"color": color, 
					"shape": shape,
					"node_name": node_name,
					"x": x, 
					"y": y
				}

	table_connection = r.db(DB_NAME).table(graphname)
	if not table_connection.get(node_name):
		table_connection.insert(node_info).run()
	else:
		table_connection.filter(r.row["node_name"] == node_name).update(node_info).run()
	
	cursor = r.db(DB_NAME).table(graphname).run()
	for d in cursor:
		pretty(d)

	return "stored successfully"

@app.route('/load/<graphname>', methods=["GET"])
def load(graphname):
	"""
		Load each node information
	"""

	return []
if __name__ == '__main__':
	SETUPDB = True
	if SETUPDB:
		dbSetup()
	app.run(debug=True, host="localhost", port=8000)