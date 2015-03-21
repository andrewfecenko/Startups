import os
from flask import Flask, render_template, redirect, url_for, request, \
    session, flash, g
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from functools import wraps
from app import app, db, lm
from flask.ext.wtf import Form
from forms import *
from models import *
from config import MAX_SEARCH_RESULTS
from itertools import permutations
from werkzeug import secure_filename
from  sqlalchemy.sql.expression import func
import datetime
import re
import random
import string


@lm.user_loader
def load_user(id):
    return users.query.get(int(id))


@app.before_request
def load_user():
    g.user = current_user


# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            kwargs["logged_in"] = True
            return f(*args, **kwargs)
        else:
            kwargs["logged_in"] = False
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap



@app.route("/")
def home():
    return render_template("index.html", home=True, current_user=current_user)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    login_form = LoginForm()
    reg_form = RegistrationForm()
    if request.method == 'POST':
        login_form.email.data = request.form['email']
        login_form.password.data = request.form['password']
        if login_form.validate_on_submit() != False:
            session['logged_in'] = True
            user = users.query.filter_by(
                email=login_form.email.data).first()
            login_user(user)
            flash('You were just logged in!')
            return redirect(url_for('home'))

    elif request.method == 'GET':
        return render_template(
            'login.html', login_form=login_form, reg_form=reg_form,)

    return render_template(
        'login.html', error=login_form.errors, reg_form=reg_form,
        login_form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    login_form = LoginForm()
    reg_form = RegistrationForm()
    if request.method == 'POST' and reg_form.validate_on_submit() != False:
        user = users(
            email=reg_form.email.data,
            password=reg_form.password.data,
            sur_name=reg_form.lname.data,
            first_name=reg_form.fname.data)
        db.session.add(user)
        db.session.commit()
        flash('Thanks for registering')
        return redirect(url_for('login'))

    elif request.method == 'POST' and reg_form.validate_on_submit() == False:
        return render_template(
            'register.html', login_form=login_form, reg_form=reg_form,
            error=reg_form.errors)

    elif request.method == 'GET':
        return render_template('register.html', reg_form=reg_form, error=error)

@app.route("/user")
@login_required
def user(**kwargs):
    return user_search(current_user.user_id, **kwargs)

@app.route("/add_idea")
@login_required
def add_idea(**kwargs):

    return render_template('add_idea.html', current_user=current_user)

@app.route("/logout")
@login_required
def logout(**kwargs):
    logout_user()
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('home'))