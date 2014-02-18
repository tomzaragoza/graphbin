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
		Store the node, edge into the DB. 
		Will act as a function to update the coordinates 
		of the nodes as well.
	"""
	if request.form['type'] == 'node':
		print "Storing node to DB..."
		label = request.form["label"]
		color = request.form["color"]
		shape = request.form["shape"]
		node_name = request.form["node_name"]
		graph_obj_type = request.form["type"]
		x = request.form["x"]
		y = request.form["y"]

		node_info = {
						"label": label,
						"color": color, 
						"shape": shape,
						"node_name": node_name,
						"type": graph_obj_type,
						"mass": 50,
						"fixed": True,
						"x": x, 
						"y": y
					}

		cursor = r.db(DB_NAME).table(graphname).filter(r.row["node_name"] == node_name).run()
		if len(list(cursor)) == 0:
			print "Insert node {0}".format(node_name)
			r.db(DB_NAME).table(graphname).insert(node_info).run()
		else:
			print "Update node {0}".format(node_name)
			r.db(DB_NAME).table(graphname).filter(r.row["node_name"] == node_name).update(node_info).run()

		# Printing out all the documents in the table
		# cursor = r.db(DB_NAME).table(graphname).run()
		# for d in cursor:
		# 	pretty(d)
	elif request.form['type'] == 'edge':
		print "Storing edge to DB..."
		source = request.form["source"]
		target = request.form["target"]
		edge_name = request.form["name"] # something like "n1 to n2", etc.

		edge_info = {
						"source": source,
						"target": target,
						"edge_name": edge_name,
						"type": "edge"
					}

		cursor = r.db(DB_NAME).table(graphname).filter(r.row["edge_name"] == edge_name).run()
		if len(list(cursor)) == 0:
			print "Inserting edge {0}".format(edge_name)
			r.db(DB_NAME).table(graphname).insert(edge_info).run()
		else:
			print "Updating edge {0}".format(edge_name)
			r.db(DB_NAME).table(graphname).filter(r.row["edge_name"] == edge_name).update(edge_info).run()


	return "stored {0} successfully".format(request.form['type'])

@app.route('/load/<graphname>', methods=["GET"])
def load(graphname):
	""" Load each node, edge information """

	all_nodes = []
	cursor_nodes = r.db(DB_NAME).table(graphname).filter(r.row["type"] == "node").run()
	for d in cursor_nodes:
		del d['id']
		d['node_name'] = str(d['node_name'])
		d['color'] = str(d['color'])
		d['shape'] = str(d['shape'])
		d['label'] = str(d['label'])
		d['mass'] = int(d['mass']) if 'mass' in d else 50
		d['fixed'] = bool(d['fixed']) if 'fixed' in d else True
		d['x'] = float(d['x'])
		d['y'] = float(d['y'])

		all_nodes.append(d)
	
	all_edges =[]
	cursor_edge = r.db(DB_NAME).table(graphname).filter(r.row["type"] == "edge").run()
	for d in cursor_edge:
		del d['id']
		d['source'] = str(d['source'])
		d['target'] = str(d['target'])
		all_edges.append(d)

	# print "All the nodes"
	# pretty(all_nodes)
	# print
	# print "All the edges"
	# pretty(all_edges)

	return jsonify(nodes=all_nodes, edges=all_edges)

@app.route('/delete/<graphname>', methods=["POST"])
def delete(graphname):

	node_name = request.form["node_name"]
	edges_to_delete = request.form["edges_to_delete"].split(',')

	for edge_name in edges_to_delete:
		r.db(DB_NAME).table(graphname).filter(r.row["edge_name"] == edge_name).delete().run()

	r.db(DB_NAME).table(graphname).filter(r.row["node_name"] == node_name).delete().run()

	return "succesfully deleted node {0} and its edges".format(node_name)
if __name__ == '__main__':
	SETUPDB = True
	if SETUPDB:
		dbSetup()
	app.run(debug=True, host="localhost", port=8000)