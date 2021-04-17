import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Games(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'games'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    price = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    developers = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    release_date = sqlalchemy.Column(sqlalchemy.Date, nullable=True)
    ratio = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    is_selling = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
