import datetime
import random

import flask
import flask_login
from flask_login import LoginManager
from data import db_session, news_api
from data.forms.user import RegisterForm, LoginForm
from data.forms.jobs import JobsForm
from data.users import User
from data.games import Games

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("data/db/mars_one.db")
    app.register_blueprint(news_api.blueprint)
    app.run()


def add():
    db_session.global_init('data/db/mars_one.db')
    db_sess = db_session.create_session()
    job = Games()
    job.team_leader = 1
    job.job = 'deployment of residential modules 1 and 2'
    job.work_size = 15
    job.collaborators = '2, 3'
    job.start_date = datetime.datetime.now()
    job.is_finished = False
    db_sess.add(job)
    db_sess.commit()


def add1():
    db_sess = db_session.create_session()
    cap = User()
    cap.surname = 'Scott'
    cap.name = 'Ridley'
    cap.age = 21
    cap.position = 'captain'
    cap.speciality = 'research engineer'
    cap.address = 'module_1'
    cap.email = 'scott_chief@mars.org'
    db_sess.add(cap)
    for i in range(5):
        user = User()
        user.surname = 'H' + 'a' * i + 'll'
        user.name = 'Joe'
        user.age = 18 + i * 3
        user.position = 'recruit'
        user.speciality = random.choice(['Pilot', 'Biologist', 'Mechanic', 'Astronomer', 'Programmer'])
        user.address = f'module_{i + 1}'
        user.email = f'{user.name}.{user.surname}@mars.org'
        db_sess.add(user)
    db_sess.commit()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            flask_login.login_user(user, remember=form.remember_me.data)
            return flask.redirect("/")
        return flask.render_template('login.html',
                                     message="Неправильный логин или пароль",
                                     form=form)
    return flask.render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return flask.redirect("/")


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Games).all()
    return flask.render_template("index.html", jobs=jobs)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
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
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return flask.redirect('/login')
    return flask.render_template('register.html', title='Регистрация', form=form)


@app.route('/jobs', methods=['GET', 'POST'])
@flask_login.login_required
def add_news():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Games()
        jobs.job = form.job.data
        jobs.team_leader = form.team_leader.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.start_date = form.start_date.data
        jobs.end_date = form.end_date.data
        jobs.is_finished = form.is_finished.data
        flask_login.current_user.news.append(jobs)
        db_sess.merge(flask_login.current_user)
        db_sess.commit()
        return flask.redirect('/')
    return flask.render_template('jobs.html', title='Добавление работы',
                                 form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def edit_news(id):
    form = JobsForm()
    if flask.request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(Games).filter(Games.id == id,
                                          Games.user == flask_login.current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            flask.abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(Games).filter(Games.id == id,
                                          Games.user == flask_login.current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return flask.redirect('/')
        else:
            flask.abort(404)
    return flask.render_template('jobs.html',
                                 title='Редактирование новости',
                                 form=form
                                 )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@flask_login.login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(Games).filter(Games.id == id,
                                      Games.user == flask_login.current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        flask.abort(404)
    return flask.redirect('/')


@app.errorhandler(404)
def not_found(error):
    return flask.make_response(flask.jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
