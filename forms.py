from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

# User Account related forms
class RegisterForm(Form):
	username 	= TextField(u'Username', validators = [Length(min=6, max=50)])
	email       = TextField(u'Email (optional, must be unique)', validators = [Length(min=5, max=40)])
	password    = PasswordField(u'Password', validators = [DataRequired(), Length(min=6, max=40)])
	confirm     = PasswordField(u'Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(Form):
	username        = TextField(u'Username', [DataRequired()])
	password    = PasswordField(u'Password', [DataRequired()])
