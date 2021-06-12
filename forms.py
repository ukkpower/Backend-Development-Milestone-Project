from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import InputRequired, Email, Length, ValidationError


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(
        max=15)], render_kw={"placeholder": "Enter Username"})
    password = PasswordField("Password", validators=[InputRequired(), Length(
        max=50)], render_kw={"placeholder":  "Password"})
    submit = SubmitField("Sign in")
