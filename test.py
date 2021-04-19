import requests
import json
from data.users import User


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


add1()
# print(requests.get('http://127.0.0.1:5000/api/games/1').json())
