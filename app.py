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
def public():
    polls = mongo.db.polls.find()
    return render_template("public.html", polls=polls)


@app.route("/new", methods=["GET", "POST"])
def new():
    form = NewPollForm()
    if request.method == "POST":
        poll = {
            "question": request.form.get("question"),
            "pollQuestions": {
                "pollOption_1": {
                    "option": request.form.get("pollOption_1"),
                    "votes": 0
                },
                "pollOption_2": {
                    "option": request.form.get("pollOption_2"),
                    "votes": 0
                }            
            },
            "created": datetime.utcnow()
        }
        mongo.db.polls.insert_one(poll)

    return render_template("new.html", form=form)


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
                    session["user"] = request.form.get("username").lower()
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


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
