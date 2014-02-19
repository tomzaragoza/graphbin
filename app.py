from flask import *
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from models import User
from forms import RegisterForm, LoginForm
from hash_helpers import hash_password, hash_email

# from pprint import pprint as pretty

import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

import os

app = Flask(__name__)
app.secret_key = '8yK6_Mf2D_-R6GB3C1222o1ix98o-YR_'

login_manager = LoginManager()
login_manager.init_app(app)

RDB_HOST =  os.environ.get('RDB_HOST') or 'localhost'
RDB_PORT = os.environ.get('RDB_PORT') or 28015
DB_MAIN = "graphbox"
DB_USERS = "users"
rethink = r.connect("localhost", 28015).repl()

# ---------
# DB setup
# ---------
def dbSetup():
	connection = r.connect(host=RDB_HOST, port=RDB_PORT)
	try:
		r.db_create(DB_MAIN).run(connection)
		# r.db(DB_MAIN).table_create('todos').run(connection)
		print 'Database {0} setup completed. Now run the app without --setup.'.format(DB_MAIN)
	except RqlRuntimeError:
		print 'App database {0} already exists. Run the app without --setup.'.format(DB_MAIN)

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
	user.username = user_object['username']
	user.password = user_object['password']
	user.email = user_object['email']
	user.site_id = user_object['site_id']
	user = User()
	return user


@login_manager.user_loader
def load_user(userid):
	# return User.get(userid)
	
	user_object = r.db(DB_USERS).table(userid).get(userid)#.local.users.find_one({ 'user_id': userid })
	user_session_object = load_user_from_db(user_object)

	if not type(user_object) is None and not type(user_session_object) is None:
		return user_session_object#.get_id()


# -------------------------
# Login and Register views
# -------------------------
@app.route('/register', methods=['POST', 'GET'])
def register():

	if request.method == 'POST':
		form = request.form
		hashed_email = unicode(hash_email(form['email']))
		print form['email']
		try:
			#Look into indexes for tables. This doesn't seem to be the best way
			#to check if a table exists

			r.db(DB_MAIN).table(hashed_email).run() #if runs, name already exists
			form = RegisterForm(request.form)
			flash("Email already exists! Try again")

			return render_template('register', form=form)
		except RqlRuntimeError: # Does not exist, gives error above, thus we can make user

			r.db(DB_USERS).table_create(hashed_email).run()
			r.db(DB_USERS).table(hashed_email).index_create("site_id").run()
			r.db(DB_USERS).table(hashed_email).index_wait("site_id").run()

			new_user = {}
			new_user['email'] = form['email']
			new_user['user_id'] = form['email']
			new_user['password'] = hash_password(form['email'], form['password'])
			new_user['site_id'] = hashed_email # just the email hashed

			r.db(DB_USERS).table(new_user['site_id']).insert(new_user).run()
			r.db(DB_MAIN).table_create(new_user['site_id']).run() #associated with site_id in DB_USERS
			r.db(DB_MAIN).table(new_user['site_id']).index_create("site_id").run()
			r.db(DB_MAIN).table(new_user['site_id']).index_wait("site_id").run()
			flash('Thanks for registering! Wanna login?')

			return redirect(url_for('login'))

	elif request.method == 'GET':
		form = RegisterForm(request.form)
		return render_template('register.html', form = form)

@app.route('/login', methods=['POST', 'GET'])
def login():

	if request.method == 'POST':
		form = request.form
		hashed_email = unicode(hash_email(form['email']))

		try:
			print "in the try for login"
			# if run, name already exists
			user_object = None
			user_object_cursor = r.db(DB_USERS).table(hashed_email).get_all(hashed_email, index="site_id").run()
			for d in user_object_cursor:
				print d
				user_object = d

			print "after making the user object"
			entered_password = hash_password(form['email'], form['password'])
			print "got the entered password"
			print entered_password
			print user_object['password']
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
				return render_template('login.html', form=form)

		except RqlRuntimeError:
			form = LoginForm(request.form)
			print "incorrect username or password! try again"
			return render_template('login.html', form=form)
		
	else:
		form = LoginForm(request.form)                
		return render_template('login.html', form = form)


# --------------------
# Application Routing
# --------------------
@app.route('/')
def index():
	""" 
		Loading and serving the home page of GraphBin. 
	"""
	return render_template('index.html')

@app.route('/account')
@login_required
def account():
	""" 
		Load the user's graph collection page (account).
	"""
	print "yay you're in!"
	user = 'test@test.com'
	return render_template('account.html', user = user)

@app.route('/graph/<graphname>')
@login_required
def graph(graphname):
	""" 
		Loads the graph page.
	"""
	try:
		r.db(DB_MAIN).table(graphname).run() # if this runs, graphname exists
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

		cursor = r.db(DB_MAIN).table(graphname).filter(r.row["node_name"] == node_name).run()
		if len(list(cursor)) == 0:
			print "Insert node {0}".format(node_name)
			r.db(DB_MAIN).table(graphname).insert(node_info).run()
		else:
			print "Update node {0}".format(node_name)
			r.db(DB_MAIN).table(graphname).filter(r.row["node_name"] == node_name).update(node_info).run()

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

		cursor = r.db(DB_MAIN).table(graphname).filter(r.row["edge_name"] == edge_name).run()
		if len(list(cursor)) == 0:
			print "Inserting edge {0}".format(edge_name)
			r.db(DB_MAIN).table(graphname).insert(edge_info).run()
		else:
			print "Updating edge {0}".format(edge_name)
			r.db(DB_MAIN).table(graphname).filter(r.row["edge_name"] == edge_name).update(edge_info).run()


	return "stored {0} successfully".format(request.form['type'])

@app.route('/load/<graphname>', methods=["GET"])
@login_required
def load(graphname):
	""" 
		Load each node, edge information.
	"""

	all_nodes = []
	cursor_nodes = r.db(DB_MAIN).table(graphname).filter(r.row["type"] == "node").run()
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
	cursor_edge = r.db(DB_MAIN).table(graphname).filter(r.row["type"] == "edge").run()
	for d in cursor_edge:
		del d['id']
		d['source'] = str(d['source'])
		d['target'] = str(d['target'])
		all_edges.append(d)

	return jsonify(nodes=all_nodes, edges=all_edges)

@app.route('/delete/<graphname>', methods=["POST"])
@login_required
def delete(graphname):
	""" 
		Delete node from database
	"""

	node_name = request.form["node_name"]
	edges_to_delete = request.form["edges_to_delete"].split(',')

	for edge_name in edges_to_delete:
		r.db(DB_MAIN).table(graphname).filter(r.row["edge_name"] == edge_name).delete().run()

	r.db(DB_MAIN).table(graphname).filter(r.row["node_name"] == node_name).delete().run()

	return "succesfully deleted node {0} and its edges".format(node_name)


if __name__ == '__main__':
	SETUPDB = True
	if SETUPDB:
		dbSetup()
	app.run(debug=True, host="localhost", port=8000)