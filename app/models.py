from app import db, bcrypt
from app import app
import datetime
from sqlalchemy import UniqueConstraint
from sqlalchemy import CheckConstraint
from sqlalchemy import Enum
from sqlalchemy import exc
import sys

class users(db.Model):
	"""docstring for users"""
	__table_args__ = {'extend_existing': True}
	__tablename__ = 'users'

	user_id=db.Column(db.Integer, primary_key=True,nullable=False)
	sur_name=db.Column(db.String(50),nullable=False)
	first_name=db.Column(db.String(50),nullable=False)
	email=db.Column(db.String(50),nullable=False)
	blurb=db.Column(db.Text,nullable=True)
	activated=db.Column(db.Boolean)
	password=db.Column(db.String(1000),nullable=False)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False
		
	def get_id(self):
		return unicode(self.user_id)

	def __init__(self, password, email, sur_name, first_name):
		self.password=bcrypt.generate_password_hash(password)
		self.email=email
		self.sur_name=sur_name.capitalize()
		self.first_name=first_name.capitalize()

class ideas(db.Model):
	"""docstring for ideas"""
	__table_args__ = {'extend_existing': True}
	__tablename__ = 'ideas'

	idea_id=db.Column(db.Integer, primary_key=True,nullable=False)
	idea_name=db.Column(db.String(50),nullable=False)
	desc=db.Column(db.String(1000),nullable=False)
	likes=db.Column(db.Integer,nullable=False)

	def __init__(self, idea_name, desc, likes=0):
		self.idea_name=idea_name.capitalize()
		self.desc = desc.capitalize()
		self.likes = likes




