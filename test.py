import requests
import json
import random
import datetime
from data.comment import Comment
from data import db_session


def add1():
    game = {
        'name': 'Last of ass 3',
        'price': 420,
        'description': 'трогательная история про бодибилдершу с клюшкой и девушку с татуировкой мотылька',
        'developers': 'Susny Entertainment',
        'release_date': '12.06.2020',
        'ratio': 3.5,
        'is_selling': True,
        'genre': 3
    }
    res = requests.post('http://127.0.0.1:5000/api/games', json=game).json()
    print(res)


def add():
    user = User(
        nick='Some',
        email='some@mail.ru'
    )
    res = requests.post('http://127.0.0.1:5000/api/users', json=user).json()
    print(res)


db_session.global_init('data/db/main.db')
db = db_session.create_session()
com = Comment(
    body='hello, fuckers2!',
    user_id=2,
    game_id=1
)
db.add(com)
db.commit()
x = list(filter(lambda s: comm.user_id == s.id, users))[0]
