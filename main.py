import datetime
import random
import requests 

import flask
import flask_login
import flask_restful
from flask import request
from data import db_session
from data.forms import loginform, registerform
from data.users import User
from data.games import Game
from data import users_resources
from data import games_resources
from werkzeug.security import generate_password_hash, check_password_hash


app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = flask_restful.Api(app)
login_manager = flask_login.LoginManager(app)
login_manager.init_app(app)


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
    return flask.render_template("index.html", spin_games=spin_games[:3], home_games=home_games[:5])


@app.route('/cart')
def cart():
    ids = flask.session.get('cart', None)
    print(ids)
    if ids is None:
        cart_list = []
    else:
        games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
        print(games)
        cart_list = list(filter(lambda x: x['id'] in ids, games))
        print(cart_list)
    return flask.render_template('cart.html', cart_list=cart_list)


# это функция для удаления новости из корзины
# просто перенаправь на эту страницу по кнопке удалить из корзины
@app.route('/cart_delete/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def news_delete(id):
    flask.session['cart'].pop(flask.session['cart'].index(id))
    return flask.redirect('/cart')


# это функция для добавление новости в корзину
# просто перенаправь на эту страницу по кнопке добавить в корзину
@app.route('/cart_add/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def news_add(id):
    if id not in flask.session['cart']:
        flask.session['cart'].append(id)
    return flask.redirect('/cart')


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
        return flask.redirect('/')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/list')
@flask_login.login_required
def game_list():
    games = requests.get('http://127.0.0.1:5000/api/games').json()['games']
    games_list = list(filter(lambda x: x['img'] is not None, games))
    random.shuffle(games_list)
    return flask.render_template('list.html', games_list=games_list)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect("/login")


@app.route('/admin')
@flask_login.login_required
def admin():
    return flask.redirect('list')
# всё это пока не нужно без шаблонов, так что пусть лежит
# @app.route('/news/<int:id>', methods=['GET', 'POST'])
# @flask_login.login_required
# def edit_news(id):
#     form = JobsForm()
#     if flask.request.method == "GET":
#         db_sess = db_session.create_session()
#         news = db_sess.query(Games).filter(Games.id == id,
#                                           Games.user == flask_login.current_user
#                                           ).first()
#         if news:
#             form.title.data = news.title
#             form.content.data = news.content
#             form.is_private.data = news.is_private
#         else:
#             flask.abort(404)
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#         news = db_sess.query(Games).filter(Games.id == id,
#                                           Games.user == flask_login.current_user
#                                           ).first()
#         if news:
#             news.title = form.title.data
#             news.content = form.content.data
#             news.is_private = form.is_private.data
#             db_sess.commit()
#             return flask.redirect('/')
#         else:
#             flask.abort(404)
#     return flask.render_template('jobs.html',
#                                  title='Редактирование новости',
#                                  form=form
#                                  )


# @app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
# @flask_login.login_required
# def news_delete(id):
#     db_sess = db_session.create_session()
#     news = db_sess.query(Games).filter(Games.id == id,
#                                       Games.user == flask_login.current_user
#                                       ).first()
#     if news:
#         db_sess.delete(news)
#         db_sess.commit()
#     else:
#         flask.abort(404)
#     return flask.redirect('/')


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    # запускаем приложение
    main()
