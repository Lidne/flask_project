import datetime
import random
import requests
import string
import Levenshtein
import os

import flask
import flask_login
import flask_restful
from flask_ngrok import run_with_ngrok
from flask_login import current_user
from flask import request, url_for
from data import db_session
from data.forms import loginform, registerform, searchform, commentform, gayform
from data.users import User
from data.games import Game
from data.comment import Comment
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
    """Функция, инициаилизирующая api и базу данных"""
    # connecting to a database
    db_session.global_init("data/db/main.db")
    # доавляем api в приложение для использования в дальнейшем
    # api для пользователей
    api.add_resource(users_resources.UsersListResource, '/api/users')
    api.add_resource(users_resources.UsersResource, '/api/users/<int:user_id>')
    # api для игр
    api.add_resource(games_resources.GamesListResource, '/api/games')
    api.add_resource(games_resources.GamesResource, '/api/games/<int:game_id>')
    app.run()  # запускаем приложение


@app.route("/", methods=['GET', 'POST'])
def index():
    """Функция зугружает главную страницу"""
    form = searcher()  # форма для поиска
    if form.__class__.__name__ != 'SearchForm':
        return form
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']  # пол
    spin_games = list(filter(lambda x: x['img_wide'] is not None, games))
    random.shuffle(spin_games)
    home_games = list(filter(lambda x: x['img'] is not None, games))
    random.shuffle(home_games)
    return flask.render_template("index.html", spin_games=spin_games[:3], home_games=home_games[:4],
                                 form_s=form)


@app.route('/list', methods=['GET', 'POST'])
def game_list():
    """Функция загружает полный список игр"""
    form = searcher()
    if form.__class__.__name__ != 'SearchForm':
        return form
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    games_list = list(filter(lambda x: x['img'] is not None, games))
    random.shuffle(games_list)
    return flask.render_template('list.html', games_list=games_list, form_s=form)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    """Функция загружает корзину"""
    form = searcher()
    if form.__class__.__name__ != 'SearchForm':
        return form
    ids = flask.session.get('cart', None)  # получаем значения из сессии
    if ids is None:  # если в сессии пусто, то игры не выводим
        cart_list = []
    else:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']  # получем список игр
        cart_list = list(filter(lambda x: x['id'] in ids, games))
    return flask.render_template('cart.html', cart_list=cart_list, form_s=form)


@app.route('/cart_delete/<int:id>', methods=['GET', 'POST'])
def cart_delete(id):
    """Функция удаляет из корзины игру по id"""
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
    """Функция возвращает адрес, с которого мы пришли"""
    return request.args.get('next') or \
           request.referrer or \
           flask.url_for(default)


@app.route('/cart_add/<int:id>', methods=['GET', 'POST'])
def cart_add(id):
    """Функция добавляет игру в корзину"""
    cart1 = flask.session.get('cart', None)
    if cart1 is None:
        cart1 = [id]
    elif id not in cart1:
        cart1.append(id)
    flask.session['cart'] = cart1
    return flask.redirect('/cart')


@app.route('/<int:game_id>', methods=['GET', 'POST'])
def game(game_id):
    """Функция загружает страницу игры"""
    form = searcher()
    if form.__class__.__name__ != 'SearchForm':
        return form
    sess = db_session.create_session()
    res = requests.get(f'http://127.0.0.1:5000/api/games/{game_id}').json()['game']
    res['genre'] = sess.query(Genres.genre).filter(res['genre'] == Genres.id).first()[0]
    comments = sess.query(Comment).filter(Comment.game_id == game_id).all()
    for i in comments:
        i.username = sess.query(User.nick).filter(User.id == i.user_id).first()[0]
    return flask.render_template('product.html', game=res, form_s=form, comments=comments)


@app.route('/add_comment/<int:game_id>', methods=['GET', 'POST'])
@flask_login.login_required
def add_comment(game_id):
    """Функция добавляет комментарий через форму"""
    form = commentform.CommentForm()
    if request.method == 'POST':
        sess = db_session.create_session()
        comm = Comment(
            body=form.body.data,
            user_id=current_user.id,
            game_id=game_id
        )
        sess.add(comm)
        sess.commit()
        return flask.redirect(f'/{game_id}')
    return flask.render_template('comments.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Функция логирует пользователя"""
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
    """Функция регистрирует пользователя"""
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


@app.route('/add_game', methods=['GET', 'POST'])
@flask_login.login_required
def add_game():
    """Функция загружает шаблон для добавления игры"""
    if not current_user.admin:
        return flask.redirect('/')
    form = gayform.GameForm()
    if request.method == 'POST':
        genre = int(''.join(list(filter(lambda x: x.isdigit(), list(form.genre.data)))))
        game = Game(
            name=form.name.data,
            ratio=form.ratio.data,
            price=int(form.price.data),
            description=form.description.data,
            developers=form.developers.data,
            release_date=form.release_date.data,
            genre=genre
            )
        requests.post('http://127.0.0.1:5000/api/games', data=game.to_dict())
    return flask.render_template('add_game.html', form=form)


@app.route('/buy')
@flask_login.login_required
def buy():
    """Функция загружает форму для покупки игр из корзины"""
    ids = flask.session.get('cart', None)
    if ids is not None and ids:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        cart_list = list(filter(lambda x: x['id'] in ids, games))
        total = sum(list(map(lambda x: x['price'], cart_list)))
        return flask.render_template('payment.html', cart_list=cart_list, total=total)


@app.route('/goods')
@flask_login.login_required
def goods():
    """Загружаем купленные игры с случайными кодами"""
    ids = flask.session.get('cart', None)
    if ids is not None:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        games = list(filter(lambda x: x['id'] in ids, games))
        # перемешиваем список с буквами и числами и берём срез
        text = list(string.ascii_uppercase + string.digits)
        for i in range(len(games)):
            random.shuffle(text)
            games[i]['code'] = ''.join(text[:7])
        cart_delete(0)
        return flask.render_template('goods.html', games=games)


def searcher():
    """Функция возращает список игр с похожим названием на название из формы"""
    form = searchform.SearchForm()
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    games_list = list(filter(lambda x: x['img'] is not None, games))
    if request.method == 'POST':
        matched_games = list(filter(lambda x: form.search.data.lower() in x['name'].lower(),
                                    games_list))
        matched_games.sort(key=lambda x: Levenshtein.distance(form.search.data, x['name']))
        return flask.render_template('list.html', games_list=matched_games, form=form)
    return form


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect("/login")


# хендлеры ошибок с кастомными страницами ошибок
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
