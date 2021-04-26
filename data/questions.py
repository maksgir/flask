import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Question(SqlAlchemyBase):
    __tablename__ = 'questions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    question = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    form_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("forms.id"))
    form = orm.relation('Forms')
    answer = orm.relation("Answer", back_populates='question')
