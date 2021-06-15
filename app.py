import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import LoginForm, SignUpForm, NewPollForm
import sys

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return user_id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/public")
@app.route("/public/<page_number>", methods=['GET', 'POST'])
def public(page_number=1):
    # Number of results per page
    PAGE_LIMIT = 1
    # URL arguments passed as strings, need to convert to int for query
    page_number = int(page_number)

    filter = {"public": True}
    # Page count
    doc_count = mongo.db.polls.count_documents(filter)
    page_count = round(doc_count / PAGE_LIMIT)
    polls = list(mongo.db.polls.find(filter).sort([['_id', -1]]).skip((page_number-1)*PAGE_LIMIT).limit(PAGE_LIMIT))
    for poll in polls:
        poll['timeSince'] = time_since(poll['created'])

    return render_template(
        "public.html",
        polls=polls,
        page_number=page_number,
        page_count=page_count)


@app.route("/new", methods=["GET", "POST"])
def new():
    form = NewPollForm()
    if request.method == "POST":
        pollOptions = request.form.getlist('pollOption')
        poll = {
            "question": request.form.get("pollQuestion"),
            "totalVotes": 0,
            "pollQuestions": {},
            "public": False,
            "user_id": None,
            "created": datetime.utcnow(),
            "userFullName": "anonymous"
        }
        if not session.get("user") is None:
            poll["user_id"] = session["user"]["id"]
            poll["userFullName"] = session["user"]["name"]
        for i, val in enumerate(pollOptions):
            if val:
                poll["pollQuestions"][f"pollOption_{i}"] = {
                    'option': val,
                    'votes': 0
                    }

        _id = mongo.db.polls.insert_one(poll)
        return redirect(url_for("poll", poll_id=_id.inserted_id))

    return render_template("new.html", form=form)


@app.route("/poll/<poll_id>", methods=["GET", "POST"])
def poll(poll_id):
    poll = mongo.db.polls.find_one({"_id": ObjectId(poll_id)})
    poll['timeSince'] = time_since(poll['created'])
    if request.method == "POST":
        for key, val in poll['pollQuestions'].items():
            if key == request.form.get('pollOption'):
                val['votes'] = val['votes'] + 1
                poll['totalVotes'] = poll['totalVotes'] + 1
                mongo.db.polls.update({"_id": ObjectId(poll_id)}, poll)
                return redirect(url_for("results", poll_id=poll_id))

    return render_template("poll.html", poll=poll, type=type(poll), poll_id= ObjectId(poll_id))


@app.route("/results/<poll_id>", methods=["GET", "POST"])
def results(poll_id):
    poll = mongo.db.polls.find_one({"_id": ObjectId(poll_id)})
    # Calculate vote percentages
    for key, val in poll['pollQuestions'].items():
        percentage = 100 * float(val['votes'])/float(poll['totalVotes'])
        val['percent'] = "{:.0f}".format(percentage)
    return render_template("results.html", poll=poll)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session['user'] = {
                        'id': str(ObjectId(existing_user['_id'])),
                        'username': existing_user['username'],
                        'name': existing_user['firstName'] + " " + existing_user['lastName']
                    }
                    return redirect(url_for("dashboard"))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password", 'error')
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password", 'error')
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists", 'error')
            return redirect(url_for("signup"))

        register = {
            "firstName": request.form.get("firstName"),
            "lastName": request.form.get("lastName"),
            "email": request.form.get("email").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "created": datetime.utcnow()
        }
        mongo.db.users.insert_one(register)

        flash("Registration Successful! You can now login")
        return redirect(url_for('login'))

    return render_template("signup.html", form=form)


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/user/dashboard")
def dashboard():
    if not session.get("user") is None:
        # grab the session user's username from db
        username = mongo.db.users.find_one(
            {"username": session["user"]["username"]})
        polls = list(mongo.db.polls.find(
            {"user_id": session["user"]["id"]}))
      
        return render_template("user/dashboard.html", username=username)

    return redirect(url_for("login"))


@app.route("/user/polls")
def userPolls():
    if not session.get("user") is None:
        # grab the session user's username from db
        username = mongo.db.users.find_one(
            {"username": session["user"]["username"]})
        polls = list(mongo.db.polls.find(
            {"user_id": session["user"]["id"]}))
        return render_template("user/polls.html", username=username)

    return redirect(url_for("login"))


@app.route("/user/votes")
def userVotes():
    if not session.get("user") is None:
        # grab the session user's username from db
        username = mongo.db.users.find_one(
            {"username": session["user"]["username"]})
        polls = list(mongo.db.polls.find(
            {"user_id": session["user"]["id"]}))
        return render_template("user/votes.html", username=username)

    return redirect(url_for("login"))


@app.route("/user/profile")
def userProfile():
    if not session.get("user") is None:
        # grab the session user's username from db
        username = mongo.db.users.find_one(
            {"user_id": session["user"]["id"]})
        return render_template("user/profile.html", username=username)

    return redirect(url_for("login"))


def time_since(created):
    now = datetime.now()
    age = now - created
    if age.days == 0:
        time = age.seconds//3600
        if time <= 1:
            time = 1
            time_text = " hour"
        else:
            time_text = " hours"
    else:
        time = age.days
        if time == 1:
            time_text = " day"
        else:
            time_text = " days"
    return str(time) + time_text


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
