import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from hashlib import md5

from .db_session import SqlAlchemyBase
"""Класс-модель комментария для базы данных"""


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    body = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime, nullable=False, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'), nullable=False)
    game_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('games.id'), nullable=False)

    games = orm.relation("User", back_populates='comment')
    users = orm.relation("Game", back_populates='comment')

