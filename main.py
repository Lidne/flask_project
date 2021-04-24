import datetime
import random
import requests
import string
import Levenshtein

import flask
import flask_login
import flask_restful
from flask_ngrok import run_with_ngrok
from flask_login import current_user
from flask import request
from data import db_session
from data.forms import loginform, registerform, searchform
from data.users import User
from data.games import Game
from data.genres import Genres
from data import users_resources
from data import games_resources

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = flask_restful.Api(app)
login_manager = flask_login.LoginManager(app)
login_manager.init_app(app)
# run_with_ngrok(app)

"""Если у вас не запускается проект, то необходимо скачать python-Levenshtein
Вот ссылка: http://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein.
Выберите последнюю версию, подходящую под вашу систему (32 или 64 бит).
После загрузки необходимо перейти в директорию, где лежит скачаный файл и запустить
через консоль команду: pip install <название скачанного файла>.
Без этого поиск по играм не заработает, а через репо устанавливать бесполезно"""


def main():
    # connecting to a database
    db_session.global_init("data/db/main.db")
    # доавляем api в приложение для использования в дальнейшем
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')
    api.add_resource(games_resources.GamesListResource, '/api/games')
    api.add_resource(games_resources.GamesResource, '/api/games/<int:game_id>')
    app.run()


@app.route("/")
def index():
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    spin_games = list(filter(lambda x: x['img_wide'] is not None, games))
    random.shuffle(spin_games)
    home_games = list(filter(lambda x: x['img'] is not None, games))
    random.shuffle(home_games)
    return flask.render_template("index.html", spin_games=spin_games[:3], home_games=home_games[:4])


@app.route('/list', methods=['GET', 'POST'])
def game_list():
    form = searchform.SearchForm()
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    games_list = list(filter(lambda x: x['img'] is not None, games))
    searcher(form)
    random.shuffle(games_list)
    return flask.render_template('list.html', games_list=games_list, form=form)


@app.route('/cart')
def cart():
    ids = flask.session.get('cart', None)
    if ids is None:
        cart_list = []
    else:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        cart_list = list(filter(lambda x: x['id'] in ids, games))
    return flask.render_template('cart.html', cart_list=cart_list)


@app.route('/cart_delete/<int:id>', methods=['GET', 'POST'])
def cart_delete(id):
    cart1 = flask.session.get('cart', None)
    if cart1 is not None:
        if id == 0:
            cart1.clear()
        else:
            cart1.pop(flask.session['cart'].index(id))
    else:
        cart1 = []
    flask.session['cart'] = cart1
    return flask.redirect(redirect_url())


def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           flask.url_for(default)


@app.route('/cart_add/<int:id>', methods=['GET', 'POST'])
def cart_add(id):
    cart1 = flask.session.get('cart', None)
    if cart1 is None:
        cart1 = [id]
    elif id not in cart1:
        cart1.append(id)
    flask.session['cart'] = cart1
    return flask.redirect('/cart')


@app.route('/<int:game_id>')
def game(game_id):
    sess = db_session.create_session()
    res = requests.get(f'http://127.0.0.1:5000/api/games/{game_id}').json()['game']
    res['genre'] = sess.query(Genres.genre).filter(res['genre'] == Genres.id).first()[0]
    return flask.render_template('product.html', game=res)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = loginform.LoginForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == form.email.data).first()
    if not user or not user.check_password(form.password.data):
        return flask.render_template('login.html',
                                     message="Неправильный логин или пароль",
                                     form=form)
    else:
        flask_login.login_user(user, remember=form.remember_me.data)
        return flask.redirect('/')
    return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = registerform.RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return flask.render_template('register.html', title='Регистрация',
                                         form=form,
                                         message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return flask.render_template('register.html', title='Регистрация',
                                         form=form,
                                         message="Такой пользователь уже есть")
        user = User(
            nick=form.nick.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        requests.post('http://127.0.0.1:5000/api/users', data=user.to_dict())
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/buy')
@flask_login.login_required
def buy():
    ids = flask.session.get('cart', None)
    if ids is not None and ids:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        cart_list = list(filter(lambda x: x['id'] in ids, games))
        total = sum(list(map(lambda x: x['price'], cart_list)))
        return flask.render_template('payment.html', cart_list=cart_list, total=total)


@app.route('/goods')
@flask_login.login_required
def goods():
    ids = flask.session.get('cart', None)
    if ids is not None:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        games = list(filter(lambda x: x['id'] in ids, games))
        text = list(string.ascii_uppercase + string.digits)
        for i in range(len(games)):
            random.shuffle(text)
            games[i]['code'] = ''.join(text[:7])
        cart_delete(0)
        return flask.render_template('goods.html', games=games)


def searcher(form):
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    games_list = list(filter(lambda x: x['img'] is not None, games))
    if request.method == 'POST':
        matched_game = min(games_list, key=lambda x: Levenshtein.distance(form.search.data, x['name']))
        flask.redirect(f'/{matched_game["id"]}')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect("/login")


@app.errorhandler(401)
def not_found(error):
    return flask.render_template('unauthorised.html', code='401',
                                 image='/static/img/brand/auth_icon.png'), 401


@app.errorhandler(404)
def not_found(error):
    return flask.render_template('error.html', error=str(error), code='404',
                                 image='/static/img/brand/error_icon.png'), 404


@app.errorhandler(500)
def server_error(error):
    return flask.render_template('error.html', error=str(error), code='500',
                                 image='/static/img/brand/cloud_icon.png'), 500


if __name__ == '__main__':
    # запускаем приложение
    main()
