import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
"""Класс-модель жанров для базы данных"""


class Genres(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False,
                           primary_key=True, autoincrement=True)
    genre = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    games = orm.relation('Game')
