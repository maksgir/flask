from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Application(FlaskForm):
    submit = SubmitField('Принять')
    questions = StringField(' ')
