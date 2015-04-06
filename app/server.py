import os
from flask import Flask, render_template, redirect, url_for, request, \
    session, flash, g, jsonify
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
import pygal
from pygal.style import LightColorizedStyle


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

@app.route("/graph")
@login_required
def get_graph(**kwargs):
    num_elements = float(len(ideas.query.all()))
    health = len(ideas.query.filter_by(industry=0).all())
    technology = len(ideas.query.filter_by(industry=1).all())
    education = len(ideas.query.filter_by(industry=2).all())
    finance = len(ideas.query.filter_by(industry=3).all())
    travel = len(ideas.query.filter_by(industry=4).all())
    pie_chart = pygal.Pie(style=LightColorizedStyle)
    pie_chart.title = 'Distribution of Industries'
    pie_chart.add('Health', 100*(health/num_elements))
    pie_chart.add('Technology', 100*(technology/num_elements))
    pie_chart.add('Education', 100*(education/num_elements))
    pie_chart.add('Finance', 100*(finance/num_elements))
    pie_chart.add('Travel', 100*(travel/num_elements))
    pie_chart.render_to_file('app/templates/temp.svg')
    return render_template("graph.html", current_user=current_user)

@app.route("/")
def home():
    return render_template("index.html", home=True, current_user=current_user)


@app.route("/login", methods=['GET', 'POST'])
def login():
    error = None
    login_form = LoginForm()
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
            'login.html', login_form=login_form)

    return render_template(
        'login.html', reg_form=reg_form, login_form=login_form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
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
            'register.html', reg_form=reg_form,
            error=reg_form.errors)

    elif request.method == 'GET':
        return render_template('register.html', reg_form=reg_form, error=error)

@app.route("/user")
@login_required
def user(**kwargs):
    return user_search(current_user.user_id, **kwargs)

@app.route("/getjson", methods=['GET', 'POST'])
@login_required
def getjson(**kwargs):
    json_form = JsonForm()
    num = request.args.get('num')
    startdate = request.args.get('startdate')
    enddate = request.args.get('enddate')
    idea_list = []
    results = []
    if request.method == 'POST' and json_form.validate_on_submit() != False:
        print ("Do nothing")
        
    if (request.method == 'POST' and json_form.num.data and json_form.startdate.data and json_form.enddate.data):
        if (json_form.num.data) >= 1:
            return redirect("/getjson?num={0}&startdate={1}&enddate={2}".format(json_form.num.data,
              json_form.startdate.data, json_form.enddate.data))
        else:
            json_form.errors['num'] = ['Must enter positive value']
    if (json_form.num.data == 0):
         json_form.errors['num'] = ['Must enter positive value']
    output = {
        'num': num,
        'startdate': str(startdate),
        'enddate': str(enddate)
    }
    if (num and startdate and enddate):
        json_form.num.data = num
        td = str(startdate).split('-')
        json_form.startdate.data = datetime.date(int(td[0]), int(td[1]), int(td[2]))
        td = str(enddate).split('-')
        json_form.enddate.data = datetime.date(int(td[0]), int(td[1]), int(td[2]))
        idea_list = ideas.query.filter(ideas.date>=startdate).filter(ideas.date<=enddate).order_by(ideas.likes.desc()).limit(int(num))
        results = []
        for idea in idea_list:
            temp_dict = {}
            temp_dict['idea_id']=idea.idea_id
            temp_dict['idea_name']=str(idea.idea_name)
            temp_dict['desc']=str(idea.desc)
            temp_dict['likes']=idea.likes
            temp_dict['owner_id']=idea.owner_id
            temp_dict['industry']=idea.industry
            temp_dict['date']=str(idea.date)
            temp_dict['tags']=str(idea.tags)
            results.append(temp_dict)

    return render_template('json.html', current_user=current_user, json_form=json_form, idea_list=idea_list, results=results, output=output)

@app.route("/view_idea")
@login_required
def view_ideas(**kwargs):
    sort_form = SortForm()
    karg = request.args.get("keyword")
    targ = request.args.get("tags")
    sort = request.args.get("sort")
    all_ideas = ideas.query
    if karg:
        if karg.isdigit():
            karg = int(karg)
            if (karg in range(1, 6)):
                all_ideas = all_ideas.filter_by(industry=karg)
                sort_form.keyword.data = karg
    if targ:
        tag = targ.split()[0]
        all_ideas = all_ideas.filter(ideas.tags.contains(tag))
        sort_form.tags.data = targ

    if sort=="1" or sort=="2":
        sort_form.sort.data = int(sort)
        if (sort=="1"):
            all_ideas = all_ideas.order_by(ideas.idea_name).order_by(ideas.likes.desc()).all()
        else:
            all_ideas = all_ideas.order_by(ideas.date).order_by(ideas.likes.desc()).all()
    else:
        all_ideas = all_ideas.order_by(ideas.idea_name).order_by(ideas.likes.desc()).all()
    idea_list = []
    for idea in all_ideas:
        temp_interest = interest.query.filter_by(idea_id=idea.idea_id).filter_by(
            user_id=current_user.user_id).first()
        display = "both"
        if temp_interest:
            if temp_interest.like == True:
                display = "down"
            if temp_interest.like == False:
                display = "up"
        temp_idea = {'likes': idea.likes,
            'id': idea.idea_id,
            'name': idea.idea_name,
            'display': display,
            'url': "keyword={0}+sort={1}+tags={2}".format(karg, sort, targ)}
        idea_list.append(temp_idea)
    return render_template('view_idea.html', current_user=current_user, idea_list=idea_list, sort_form=sort_form)

@app.route("/like")
@login_required
def like_idea(**kwargs):
    idea_id = request.args.get('id')
    val = request.args.get('val')
    url = request.args.get('url')
    url = "&".join(url.split())
    print url
    if (idea_id and (val=="0" or val=="1")):
        val = int(val)
        idea = ideas.query.filter_by(idea_id=idea_id).first()
        temp_interest = interest.query.filter_by(idea_id=idea_id).filter_by(
            user_id=current_user.user_id).first()
        if (temp_interest and idea):
            if (val == 0 and temp_interest.like==True):
                idea.likes -= 1;
                interest.query.filter_by(idea_id=idea_id).filter_by(
                    user_id=current_user.user_id).delete()
                db.session.commit()
            elif (val == 1 and temp_interest.like==False):
                idea.likes += 1;
                interest.query.filter_by(idea_id=idea_id).filter_by(
                    user_id=current_user.user_id).delete()
                db.session.commit()
        elif (idea):
            if (val == 0):
                idea.likes -= 1
                like = False
            else:
                idea.likes += 1
                like = True
            temp_interest = interest(
                idea_id=idea_id,
                user_id=current_user.user_id,
                like=like
                )
            
            db.session.add(temp_interest)
            db.session.commit()
    if any([temp.split("=")[1]=="None" for temp in url.split("&")]):
        return redirect("/view_idea")
    return redirect("/view_idea?"+url)

@app.route("/idea/<int:query>")
@login_required
def idea(query, **kwargs):
    idea = ideas.query.filter_by(idea_id=query).first()
    if (idea != None):
        options = ["Health", "Technology", "Education", "Finance", "Travel"]
        date = str(idea.date)
        output = {
            'idea': idea,
            'idea_industry': options[int(idea.industry)],
            'idea_date': date[0:date.index(".")-3]
        }
        return render_template('idea.html', current_user=current_user, **output)
    else:
        return render_template('idea.html', current_user=current_user, error="Page not found")

@app.route("/my_ideas")
@login_required
def my_ideas(**kwargs):
    idea_list = ideas.query.filter_by(owner_id=current_user.user_id).order_by(ideas.likes.desc()).all()

    return render_template('my_idea.html', current_user=current_user, idea_list=idea_list)

@app.route("/edit/<int:query>", methods=['GET', 'POST'])
@login_required
def edit(query, **kwargs):
    idea = ideas.query.filter_by(idea_id=query).filter_by(
        owner_id=current_user.user_id).first()
    add_form = AddForm()
    message = ""
    if (idea != None):
        if request.method == 'POST' and add_form.validate_on_submit() != False:
            if (add_form.delete.data):
                ideas.query.filter_by(idea_id=query).filter_by(
                  owner_id=current_user.user_id).delete()
                db.session.commit()
                return redirect("/my_ideas")

            elif (str(idea.idea_name) != str(add_form.name.data) or
                str(idea.desc) != str(add_form.desc.data) or 
                int(idea.industry) != int(add_form.keyword.data)-1 or
                str(idea.tags) != str(add_form.tags.data)):
                idea.idea_name = add_form.name.data
                idea.desc = add_form.desc.data
                idea.industry = int(add_form.keyword.data)-1
                idea.tags = add_form.tags.data
                db.session.commit()
                message = "Successfully updated!"
        
        elif request.method == 'GET':
            add_form.keyword.data = int(idea.industry)+1
            add_form.desc.data = idea.desc
            add_form.name.data = idea.idea_name
            add_form.tags.data = idea.tags
        output = {
            'idea_name': idea.idea_name,
            'idea_desc': idea.desc,
            'edit_query': query,
            'message': message
        }
        return render_template('edit_idea.html', current_user=current_user, add_form=add_form, **output)
    else:
        return render_template('idea.html', current_user=current_user, error="Page not found")


@app.route("/add_idea", methods=['GET', 'POST'])
@login_required
def add_idea(**kwargs):
    add_form = AddForm()
    if request.method == 'POST' and add_form.validate_on_submit() != False:
        idea = ideas(
            idea_name=add_form.name.data,
            desc=add_form.desc.data,
            industry=int(add_form.keyword.data)-1,
            owner=current_user.user_id,
            tags=add_form.tags.data)
        db.session.add(idea)
        db.session.commit()
        flash('Thanks for adding your idea')
        return redirect(url_for('home'))

    return render_template('add_idea.html', current_user=current_user, add_form=add_form)

@app.route("/logout")
@login_required
def logout(**kwargs):
    logout_user()
    session.pop('logged_in', None)
    flash('You were just logged out!')
    return redirect(url_for('home'))
