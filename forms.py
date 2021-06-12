from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FieldList
from wtforms.validators import InputRequired, Email, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        max=15)], render_kw={"placeholder": "Enter Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(
        max=50)], render_kw={"placeholder":  "Password"})
    submit = SubmitField("Sign in")


class SignUpForm(FlaskForm):
    firstName = StringField("FirstName", validators=[
        InputRequired()], render_kw={"placeholder": "First Name"})
    lastName = StringField("LastName", validators=[
        InputRequired()], render_kw={"placeholder": "Last Name"})
    email = StringField("Email", validators=[
        InputRequired(), Email(message="Invalid Email"), Length(
            max=50)], render_kw={"placeholder": "Email Address"})
    username = StringField("Username", validators=[InputRequired(), Length(
        max=15)], render_kw={"placeholder": "Enter Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(
        max=50)], render_kw={"placeholder":  "Password"})
    submit = SubmitField("Sign in")


class NewPollForm(FlaskForm):
    pollQuestion = TextAreaField("Question", validators=[
        InputRequired()], render_kw={"placeholder": "Question"})
    pollOption_1 = StringField("Poll Option", validators=[
        InputRequired()], render_kw={"placeholder": "Poll Option"})
    pollOption_2 = StringField("Poll Option", validators=[
        InputRequired()], render_kw={"placeholder": "Poll Option"})
    pollOption_3 = StringField("Poll Option", render_kw={"placeholder": "Poll Option"})        