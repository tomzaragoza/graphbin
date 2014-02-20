from schematics.models import Model
from schematics.types import StringType

class User(Model):
	user_id = StringType(required=True)
	# username = StringType(required=True)
	email = StringType(required=True)
	password = StringType(required=True) # remember, this is a password that is hashed
	site_id = StringType(required=True)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return True

	def get_id(self):
		return unicode(self.user_id)

	def __repr__(self):
		return '<User {0}>'.format(self.email)
