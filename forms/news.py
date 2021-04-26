from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = IntegerField('Сколько вопросов в опрос-форме')
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')