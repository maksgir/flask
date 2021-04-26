from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewAnswer(FlaskForm):
    answer = StringField(' ')
    submit = SubmitField('Принять')

