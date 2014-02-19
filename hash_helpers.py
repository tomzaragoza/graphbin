import hashlib
#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#

def hash_password(username, password):
	""" Hash dat password  """
	unique_id = hashlib.md5()
	unique_id.update(username)
	unique_id.update(password)

	return unique_id.hexdigest()

def hash_site_id(username, password, time):
	""" Create a unique hash for user siteID """
	unique_id = hashlib.md5()
	unique_id.update(username)
	unique_id.update(time)
	unique_id.update(password)

	return unique_id.hexdigest()

def hash_email(email):
	""" Hash dat username  """
	unique_id = hashlib.md5()
	unique_id.update(email)

	return unique_id.hexdigest()

if __name__ == "__main__":
	print hash_email('hithere@lol.com')
	print hash_email(u'tomdzaragoza@gmail.com')