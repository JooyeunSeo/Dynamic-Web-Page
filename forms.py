# Flask-WTF 폼
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, TextAreaField, DateTimeLocalField, BooleanField
from wtforms.validators import DataRequired, Optional, Email, Length


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=50, message='Name must be between 2 and 50 characters long.')])
    email = StringField("Email", validators=[DataRequired(), Email(message='Invalid email address')])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, message='Field must be at least 6 characters long.')])
    submit = SubmitField("Sign Up")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message='Invalid email address.')])
    password = PasswordField("Password", validators=[DataRequired(message="Please enter your password.")])
    submit = SubmitField("Log In")

##########################
class TaskForm(FlaskForm):
    text = TextAreaField('Description', validators=[DataRequired()], render_kw={"class": "form-control", "placeholder": "Type your task here.", "style": "width: 400px;"})
    due_date = DateTimeLocalField('Due Date', format='%Y-%m-%dT%H:%M', validators=[Optional()], render_kw={"class": "form-control"})
    submit = SubmitField('Add', render_kw={"class": "button small"})

##########################