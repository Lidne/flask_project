import requests
import json
from data.users import User


def add1():
    user = {
        'nick': 'Lidne',
        'email': 'play.gt.play@yandex.ru',
        'hashed_password': '123456',
        'admin': True
    }
    res = requests.post('http://127.0.0.1:5000/api/users', json=user).json()
    print(res)


add1()
