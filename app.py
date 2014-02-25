from flask import *
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from models import User
from forms import RegisterForm, LoginForm
from werkzeug.contrib.fixers import ProxyFix
from hash_helpers import hash_password, hash_username

# from pprint import pprint as pretty

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

import ayah
ayah.configure("322e978072eb0dabad2a51e05e8bb53aaa38d246", "79e8cd8c44ea4ca311815fdb165a920e0558b986")

import os
import string
import random

app = Flask(__name__)
app.secret_key = '8yK6_Mf2D_-R6GB3C1222o1ix98o-YR_'
app.wsgi_app = ProxyFix(app.wsgi_app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB_MAIN = "graphbox"
DB_USERS = "users"
DB_EMAILS = "emails" # maps emails to usernames, if an email address is entered
T_EMAILS = "emails_to_users"
DB_PUBLIC_GRAPHS = "public_graphs"
T_PUBLIC_GRAPHS = "url_to_graphs"
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
		r.db(DB_PUBLIC_GRAPHS).table_create(T_PUBLIC_GRAPHS).run()

		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_create("url").run()
		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_wait("url").run()

		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_create("user").run()
		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_wait("user").run()

		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_create("graph").run()
		r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).index_wait("graph").run()

		print 'Database {0} setup completed. Now run the app without --setup'.format(DB_PUBLIC_GRAPHS)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup'.format(DB_PUBLIC_GRAPHS)

	try:
		r.db_create(DB_USERS).run(connection)
		print 'Database {0} setup completed. Now run the app without --setup'.format(DB_USERS)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup'.format(DB_USERS)

	try:
		r.db_create(DB_EMAILS).run(connection)
		print "created DB EMAILS"
		r.db(DB_EMAILS).table_create(T_EMAILS).run()
		print "created table for DB EMAILS TEMAILS"

		r.db(DB_EMAILS).table(T_EMAILS).index_create("email").run()
		r.db(DB_EMAILS).table(T_EMAILS).index_wait("email").run()

		r.db(DB_EMAILS).table(T_EMAILS).index_create("user").run()
		r.db(DB_EMAILS).table(T_EMAILS).index_wait("user").run()

		print 'Database {0} setup completed. Now run the app without --setup'.format(DB_EMAILS)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup'.format(DB_EMAILS)
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
	user.username = user_object['username']
	user.site_id = user_object['site_id']
	return user


@login_manager.user_loader
def load_user(userid):
	user_object = None
	hashed_username = hash_username(userid)

	user_object_cursor = r.db(DB_USERS).table(hashed_username).get_all(hashed_username, index="site_id").run()
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
	ayah_html = ayah.get_publisher_html()

	if request.method == 'POST':
		form = request.form
		hashed_username = unicode(hash_username(form['username']))

		secret = form['session_secret']
		passed = ayah.score_result(secret)

		if passed:

			# check if the email exists already in the DB.
			try:
				# if len(form['email']) == 0:
				# 	raise RqlRuntimeError # this is because we can't create a DB with empty string

				email_user_object = None
				email_user_cursor = r.db(DB_EMAILS).table(T_EMAILS).get_all(form['email'], index="email").run()
				for d in email_user_cursor:
					email_user_object = d


				# r.db(DB_EMAILS).table(T_EMAILS).get_all
				# cases: crashes when empty, or exists
				if len(form['email']) == 0:
					pass
				elif len(form['email']) > 0:
					if email_user_object is not None:
						if email_user_object['email'] == form['email']:
							form = RegisterForm(request.form)
							print "Email already exists!"
							flash("Email already exists! Try again")

							return render_template('register.html', form=form, ayah_html=ayah_html)
						else:
							pass

				# else:
				# 	email_map_obj = {
				# 					'username': form['username'],
				# 					'email': form['email']
				# 				}
				# 	r.db(DB_EMAILS).table(T_EMAILS).insert(email_map_obj).run()

			except RqlRuntimeError:
				form = RegisterForm(request.form)
				print "Email already exists!"
				flash("Email already exists! Try again")

				return render_template('register.html', form=form, ayah_html=ayah_html)

			try:
				# if this runs, DB already exists with email and we continue on
				r.db_create(hashed_username).run() # this is where all graphs will be saved

				new_user = {}
				new_user['email'] = form['email'] # can be empty, but must be unique, as checked above.
				new_user['user_id'] = form['username']
				new_user['username'] = form['username']
				new_user['password'] = hash_password(form['username'], form['password'])
				new_user['site_id'] = hashed_username # just the username hashed

				r.db(DB_USERS).table_create(hashed_username).run()

				r.db(DB_USERS).table(hashed_username).insert(new_user).run()
				r.db(DB_USERS).table(hashed_username).index_create("site_id").run()
				r.db(DB_USERS).table(hashed_username).index_wait("site_id").run()

				r.db(DB_USERS).table(hashed_username).index_create("email").run()
				r.db(DB_USERS).table(hashed_username).index_wait("email").run()

				email_map_obj = {
									'username': form['username'],
									'email': form['email']
								}
				r.db(DB_EMAILS).table(T_EMAILS).insert(email_map_obj).run()

				flash('Thanks for registering! Wanna login?')

				return redirect(url_for('login'))
			except RqlRuntimeError: 
				form = RegisterForm(request.form)
				print "Username already exists!"
				flash("Email already exists! Try again")

				return render_template('register.html', form=form, ayah_html=ayah_html)
		else:
			print "You ain't no human!"
			form = RegisterForm(request.form)
			return render_template('register.html', form=form, ayah_html=ayah_html)


	elif request.method == 'GET':
		form = RegisterForm(request.form)
		return render_template('register.html', form=form, ayah_html=ayah_html)


@app.route('/login', methods=['POST', 'GET'])
def login():


	if request.method == 'POST':
		form = request.form
		hashed_username = unicode(hash_username(form['username']))

		try:
			# if run, name already exists
			user_object = None
			user_object_cursor = r.db(DB_USERS).table(hashed_username).get_all(hashed_username, index="site_id").run()
			for d in user_object_cursor:
				user_object = d

			entered_password = hash_password(form['username'], form['password'])
			if entered_password == user_object['password']: #check both hashed versions if they match
				user = User()
				user.user_id = form['username']
				user.password = entered_password
				user.site_id = hashed_username

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
		return render_template('login.html', form=form)


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


@app.route('/public_load/<public_url>', methods=["GET"])
def public_graph(public_url):

	pub_graph_cursor = r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).get_all(public_url, index="url").run()

	for doc in pub_graph_cursor:
		pub_graph_data = doc

	if pub_graph_data is not None:
		graphname = pub_graph_data['graph']
		site_id = pub_graph_data['user']

		all_nodes = []
		cursor_nodes = r.db(site_id).table(graphname).filter(r.row["type"] == "node").run()

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
		cursor_edge = r.db(site_id).table(graphname).filter(r.row["type"] == "edge").run()
		for d in cursor_edge:
			del d['id']
			d['source'] = str(d['source'])
			d['target'] = str(d['target'])
			all_edges.append(d)

		return jsonify(nodes=all_nodes, edges=all_edges)


@app.route('/<public_url>', methods=["GET"])
def public_load(public_url):

	pub_graph_cursor = r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).get_all(public_url, index="url").run()
	num_of_graphs = len(list(pub_graph_cursor))
	if num_of_graphs == 0:
		return "Nothing at that address..."
	elif num_of_graphs > 0:
		return render_template('graph_public.html', url=public_url)

@app.route('/create_graph/<graphname>', methods=["POST"])
@login_required
def create_graph(graphname):
	""" Create the graph with the given graphname"""
	db_name = current_user['site_id']
	public_association = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(8))

	r.db(db_name).table_create(graphname).run()

	public_graph_data = {
							'url': public_association,
							'user': current_user['site_id'],
							'graph': graphname,
							'type': 'mapping'
						}
	public_graph_data['access'] = public_graph_data['user'] + '+' + public_graph_data['graph']

	r.db(db_name).table(graphname).insert(public_graph_data).run()

	r.db(db_name).table(graphname).index_create("type").run()
	r.db(db_name).table(graphname).index_wait("type").run()

	r.db(db_name).table(graphname).index_create("node_name").run()
	r.db(db_name).table(graphname).index_wait("node_name").run()

	r.db(db_name).table(graphname).index_create("edge_name").run()
	r.db(db_name).table(graphname).index_wait("edge_name").run()

	# create table for user in public graphs
	r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).insert(public_graph_data).run()

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
			hashed_username = current_user['site_id']
			access_key_public_graph = hashed_username + '+' + graphname
			
			r.db(hashed_username).table_drop(graphname).run() # delete from user's DB

			pub_graph_cursor = r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).get_all(access_key_public_graph, index="access").run()
			for d in pub_graph_cursor:
				pub_graph_obj = d

			r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).get(pub_graph_obj['id']).delete().run() # delete from public graph DB

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
	# Update in DB_PUBLIC_GRAPH
	return jsonify(newName=new_name)

@app.route('/graph/<graphname>')
@login_required
def graph(graphname):
	""" 
		Loads the graph page.
	"""
	try:
		r.db(current_user['site_id']).table(graphname).run() # if this runs, graphname exists

		pub_graph_cursor = r.db(DB_PUBLIC_GRAPHS).table(T_PUBLIC_GRAPHS).get_all(graphname, index="graph").run()
		for d in pub_graph_cursor:
			pub_graph_obj = d
		return render_template('graph.html', pub_url=pub_graph_obj['url'])
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
	# app.run(debug=True, host="localhost", port=8000)
	app.run(debug=True)
