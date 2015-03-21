from flask.ext.wtf import Form, RecaptchaField
from wtforms import BooleanField, StringField, TextField, PasswordField, validators
from wtforms.validators import DataRequired,InputRequired, Email
from wtforms.fields.html5 import EmailField  
from flask.ext.login import current_user
from models import users
from server import db
from app import bcrypt

class AddForm(Form):
	name = TextField('Idea Name', [validators.required(), validators.length(max=20)])
	desc = TextField('Description', [validators.required(), validators.length(max=200)])

	def validate(self):
		if not Form.validate(self):
			return False
		else:
			return True

class LoginForm(Form):
    email = EmailField('Email Address', [validators.Required(), validators.Email(), validators.Length(min=1, max=35)])
    password = PasswordField('Password', [validators.Required()])
    
    def validate(self):
    	if not Form.validate(self):
      		return False

		
    	user = users.query.filter_by(email = self.email.data).first()
    	
    	
    	if user and bcrypt.check_password_hash(user.password, self.password.data):
    		return True
    	else:
			self.email.errors.append("Invalid e-mail or password")
			return False



class RegistrationForm(Form):
	email = EmailField('Email Address', [validators.Required(), validators.Email(), validators.Length(min=1, max=35)])
	fname = TextField('First Name', [validators.required(), validators.length(max=10)])
	lname = TextField('Last Name', [validators.required(), validators.length(max=20)])
	password = PasswordField('New Password', [validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password', [validators.Required(), validators.EqualTo('password', message='Passwords must match')])
	def validate(self):
		if not Form.validate(self):
			return False
      		
		#check if username/email is taken or not
		if users.query.filter_by(email = self.email.data).first() is not None:
			self.email.errors.append("That email is already taken")
			return False
		else:
			return True


class SearchForm(Form):
	search = StringField('search', validators=[DataRequired()])

class ResetPasswordForm(Form):
	
	old_password = PasswordField('Old Password', [validators.Required()])
	new_password = PasswordField('New Password', [validators.Required(), validators.EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField('Repeat Password', [validators.Required(), validators.EqualTo('new_password', message='Passwords must match')])
	def validate(self):
		if not Form.validate(self):
			return False
		user = users.query.filter_by(email = current_user.email).first()
		if user and user.pw == self.old_password.data:
			return True
		else:
			self.old_password.errors.append("Invalid password")
		return False

class ResetEmailForm(Form):
	
	
	password = PasswordField('Password', [validators.Required()])
	new_email = EmailField('New Email Address', [validators.Required(), validators.Email()])
	
	def validate(self):
		if not Form.validate(self):
			return False
		user = users.query.filter_by(email = current_user.email).first()
		if user and user.pw == self.password.data:
			return True
		else:
			self.password.errors.append("Invalid password")
		return False





