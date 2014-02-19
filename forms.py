from flask_wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length

# User Account related forms
class RegisterForm(Form):
	email       = TextField(u'Email', validators = [DataRequired(), Length(min=6, max=40)])
	password    = PasswordField(u'Password', validators = [DataRequired(), Length(min=6, max=40)])
	confirm     = PasswordField(u'Repeat Password', [DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(Form):
	email        = TextField(u'Email', [DataRequired()])
	password    = PasswordField(u'Password', [DataRequired()])
