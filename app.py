from flask import *
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from models import User
from forms import RegisterForm, LoginForm
from hash_helpers import hash_password, hash_email

# from pprint import pprint as pretty

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

import os
import string
import random

app = Flask(__name__)
app.secret_key = '8yK6_Mf2D_-R6GB3C1222o1ix98o-YR_'

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB_MAIN = "graphbox"
DB_USERS = "users"
DB_PUBLIC_GRAPHS = "public_graphs"
rethink = r.connect("localhost", 28015).repl()

# ---------
# DB setup
# ---------
def dbSetup():
	connection = r.connect(host=RDB_HOST, port=RDB_PORT)

	# All that matters is that DB_USERS is created
	# Each account DB will be created after a user logs in.

	# try:
	# 	r.db_create(DB_MAIN).run(connection)
	# 	# r.db(DB_MAIN).table_create('todos').run(connection)
	# 	print 'Database {0} setup completed. Now run the app without --setup.'.format(DB_MAIN)
	# except RqlRuntimeError:
	# 	print 'App database {0} already exists. Run the app without --setup.'.format(DB_MAIN)

	try:
		r.db_create(DB_PUBLIC_GRAPHS).run(connection)
		print 'Database {0} setup completed. Now run the app without --setup'.format(DB_PUBLIC_GRAPHS)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup'.format(DB_PUBLIC_GRAPHS)

	try:
		r.db_create(DB_USERS).run(connection)
		print 'Database {0} setup completed. Now run the app without --setup'.format(DB_USERS)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup'.format(DB_USERS)
	finally:
		connection.close()

# -------------
# Login stuff
# -------------
@app.before_request
def before_request():
	g.user = current_user


def load_user_from_db(user_object):
	user = User()
	user.user_id = user_object['user_id']
	user.password = user_object['password']
	user.email = user_object['email']
	user.site_id = user_object['site_id']
	return user


@login_manager.user_loader
def load_user(userid):
	user_object = None
	hashed_email = hash_email(userid)

	user_object_cursor = r.db(DB_USERS).table(hashed_email).get_all(hashed_email, index="site_id").run()
	for doc in user_object_cursor:
		user_object = doc

	user_session_object = load_user_from_db(user_object)

	if type(user_object) != None and type(user_session_object) != None:
		return user_session_object#.get_id()


# -------------------------
# Login, Logout, Register views
# -------------------------
@app.route('/register', methods=['POST', 'GET'])
def register():

	if request.method == 'POST':
		form = request.form
		hashed_email = unicode(hash_email(form['email']))

		try:
			# if this runs, DB already exists with email and we continue on
			r.db_create(hashed_email).run() # this is where all graphs will be saved

			new_user = {}
			new_user['email'] = form['email']
			new_user['user_id'] = form['email']
			new_user['password'] = hash_password(form['email'], form['password'])
			new_user['site_id'] = hashed_email # just the email hashed

			r.db(DB_USERS).table_create(hashed_email).run()

			r.db(DB_USERS).table(hashed_email).insert(new_user).run()
			r.db(DB_USERS).table(hashed_email).index_create("site_id").run()
			r.db(DB_USERS).table(hashed_email).index_wait("site_id").run()

			flash('Thanks for registering! Wanna login?')

			return redirect(url_for('login'))
		except RqlRuntimeError: 
			form = RegisterForm(request.form)
			print "Email already exists?"
			flash("Email already exists! Try again")

			return render_template('register.html', form=form)

	elif request.method == 'GET':
		form = RegisterForm(request.form)
		return render_template('register.html', form = form)


@app.route('/login', methods=['POST', 'GET'])
def login():

	if request.method == 'POST':
		form = request.form
		hashed_email = unicode(hash_email(form['email']))

		try:
			# if run, name already exists
			user_object = None
			user_object_cursor = r.db(DB_USERS).table(hashed_email).get_all(hashed_email, index="site_id").run()
			for d in user_object_cursor:
				user_object = d

			entered_password = hash_password(form['email'], form['password'])
			if entered_password == user_object['password']: #check both hashed versions if they match
				user = User()
				user.email = form['email']
				user.user_id = form['email']
				user.password = entered_password
				user.site_id = hashed_email

				login_user(user)

				return redirect(url_for('account'))
			else:
				form = LoginForm(request.form)
				print "incorrect username or password! try again"
				flash("aww ye")
				return render_template('login.html', form=form)

		except RqlRuntimeError:
			form = LoginForm(request.form)
			print "incorrect username or password! try again"
			return render_template('login.html', form=form)
		
	else:
		form = LoginForm(request.form)                
		return render_template('login.html', form = form)


@app.route('/logout')
@login_required   
def logout():
	logout_user()
	flash('See ya later!')
	return redirect(url_for('login'))

# --------------------
# Application Routing
# --------------------
@app.route('/')
def index():
	""" 
		Loading and serving the home page of GraphBin. 
	"""
	return render_template('index.html', logged_in = current_user.is_authenticated())


@app.route('/load_graph_list', methods=["POST"])
@login_required
def load_graph_list():
	""" 
		Load the list of graphs for a user.
	"""
	all_graphs = r.db(current_user['site_id']).table_list().run()
	all_graphs.sort()
	return render_template('components/account_components/account_graph_list.html', all_graphs=all_graphs)


@app.route('/account')
@login_required
def account():
	""" 
		Load the user's graph collection page (account).
	"""
	return render_template('account.html')


@app.route('/create_graph/<graphname>', methods=["POST"])
@login_required
def create_graph(graphname):
	""" Create the graph with the given graphname"""
	r.db(current_user['site_id']).table_create(graphname).run()
	return jsonify(exists=True)


@app.route('/check_graph/<graphname>', methods=["POST"])
@login_required
def check_graph(graphname):
	""" 
		Loads the graph page.
	"""
	try:
		r.db(current_user['site_id']).table(graphname).run() # if this runs, graphname exists
		return jsonify(exists=True)
	except RqlRuntimeError:
		return jsonify(exists=False)


@app.route('/delete_graph/<graphname>', methods=["GET", "POST"])
@login_required
def delete_graph(graphname):
	""" 
		Delete the selected graph IF POST.
		Render the delete graph prompt IF GET.
	"""
	if request.method == "GET":
		return render_template('components/account_components/account_delete_graph.html', graphname=graphname)
	elif request.method == "POST":
		try:
			r.db(current_user['site_id']).table_drop(graphname).run()
			return jsonify(deleted=True)
		except RqlRuntimeError:
			return jsonify(deleted=False)


@app.route('/graph_settings/<graphname>', methods=["GET"])
def graph_settings(graphname):
	""" 
		Load the prompt for settings in the graph. 
	"""
	return render_template('components/account_components/account_graph_settings.html', graphname=graphname)


@app.route('/rename_graph/<old_graphname>', methods=["POST"])
def rename_graph(old_graphname):
	""" 
		Rename the selected graph
	"""

	db_name = current_user['site_id'] # it's just used multiple times in this view

	new_name = request.form['newName']
	r.db(db_name).table_create(new_name).run()
	r.db(db_name).table(new_name).insert(r.db(db_name).table(old_graphname)).run()
	r.db(db_name).table_drop(old_graphname).run()
	return jsonify(newName=new_name)

@app.route('/graph/<graphname>')
@login_required
def graph(graphname):
	""" 
		Loads the graph page.
	"""
	try:
		r.db(current_user['site_id']).table(graphname).run() # if this runs, graphname exists
		return render_template('graph.html')
	except RqlRuntimeError:
		return "Error: Graph '{0}'' does not exist".format(graphname)


@app.route('/store/<graphname>', methods=["POST"])
@login_required
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

		node_info = {
						"label": label,
						"color": color, 
						"shape": shape,
						"node_name": node_name,
						"type": graph_obj_type,
						"mass": 50,
						"fixed": True
					}

		if "x" in request.form:
			node_info['x'] = request.form["x"]
		if "y" in request.form:
			node_info['y'] = request.form["y"]

		cursor = r.db(current_user['site_id']).table(graphname).filter(r.row["node_name"] == node_name).run()
		if len(list(cursor)) == 0:
			print "Insert node {0}".format(node_name)
			r.db(current_user['site_id']).table(graphname).insert(node_info).run()
		else:
			print "Update node {0}".format(node_name)
			r.db(current_user['site_id']).table(graphname).filter(r.row["node_name"] == node_name).update(node_info).run()

	elif request.form['type'] == 'edge':
		print "Storing edge to DB..."
		source = request.form["source"]
		target = request.form["target"]
		edge_name = request.form["edge_name"] # something like "n1 to n2", etc.

		edge_info = {
						"source": source,
						"target": target,
						"edge_name": edge_name,
						"type": "edge"
					}

		cursor = r.db(current_user['site_id']).table(graphname).filter(r.row["edge_name"] == edge_name).run()
		if len(list(cursor)) == 0:
			print "Inserting edge {0}".format(edge_name)
			r.db(current_user['site_id']).table(graphname).insert(edge_info).run()
		else:
			print "Updating edge {0}".format(edge_name)
			r.db(current_user['site_id']).table(graphname).filter(r.row["edge_name"] == edge_name).update(edge_info).run()


	return "stored {0} successfully".format(request.form['type'])


@app.route('/load/<graphname>', methods=["GET"])
@login_required
def load(graphname):
	""" 
		Load each node, edge information.
	"""

	all_nodes = []
	cursor_nodes = r.db(current_user['site_id']).table(graphname).filter(r.row["type"] == "node").run()
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
	cursor_edge = r.db(current_user['site_id']).table(graphname).filter(r.row["type"] == "edge").run()
	for d in cursor_edge:
		del d['id']
		d['source'] = str(d['source'])
		d['target'] = str(d['target'])
		all_edges.append(d)

	return jsonify(nodes=all_nodes, edges=all_edges)


@app.route('/delete_node/<graphname>', methods=["POST"])
@login_required
def delete_node(graphname):
	""" 
		Delete node from database
	"""

	node_name = request.form["node_name"]
	edges_to_delete = request.form["edges_to_delete"].split(',')

	for edge_name in edges_to_delete:
		r.db(current_user['site_id']).table(graphname).filter(r.row["edge_name"] == edge_name).delete().run()

	r.db(current_user['site_id']).table(graphname).filter(r.row["node_name"] == node_name).delete().run()

	return "succesfully deleted node {0} and its edges".format(node_name)

@app.route('/delete_edge/<graphname>', methods=["POST"])
@login_required
def delete_edge(graphname):
	""" 
		Delete the edges in the DB.
		Note that the edge selected might not exist in the DB.
	"""
	# Need to check vice versa of edges if it exists and delete both
	edge_name = request.form["edge_name"]
	reversed_edge_name = request.form['target'] + ' to ' + request.form['source']

	edge_name_deleted = False
	reversed_edge_name_deleted = False

	db_name = current_user['site_id']
	# Try first for the edge_name of the selected nodes in order
	try:
		r.db(db_name).table(graphname).filter(r.row['edge_name'] == edge_name).delete().run()
		edge_name_deleted = True
	except RqlRuntimeError:
		print "Edge {0} does not exist".format(edge_name)

	# Next, try the reversed edge_name of the selected nodes in reversed order
	try:
		r.db(db_name).table(graphname).filter(r.row['edge_name'] == reversed_edge_name).delete().run()
		reversed_edge_name_deleted = True
	except RqlRuntimeError:
		print "Edge {0} does not exist".format(reversed_edge_name)

	if edge_name_deleted and reversed_edge_name_deleted:
		return jsonify(deleted=True, name=edge_name, reversedEdgeName=reversed_edge_name)
	else:
		return jsonify(deleted=False, name=edge_name, reversedEdgeName=reversed_edge_name)



if __name__ == '__main__':
	SETUPDB = True
	if SETUPDB:
		dbSetup()
	app.run(debug=True, host="localhost", port=8000)