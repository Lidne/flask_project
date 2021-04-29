from flask_wtf import FlaskForm
from data.genres import Genres
from data import db_session
from wtforms import StringField, PasswordField, SelectField, SubmitField, IntegerField, TextAreaField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Email, InputRequired

db_session.global_init('data/db/main.db')
sess = db_session.create_session()
genres = sess.query(Genres.id, Genres.genre).all()


class GameForm(FlaskForm):
    name = StringField('Название', validators=[InputRequired()])
    price = IntegerField('Цена', validators=[InputRequired()])
    description = TextAreaField('Описание')
    developers = StringField('Разработчики', validators=[InputRequired()])
    release_date = StringField('Дата', validators=[InputRequired()])
    genre = SelectField('Жанр', validators=[InputRequired()], choices=genres)
    img = FileField('Изображение', validators=[FileRequired()])
    img_wide = FileField('Широкое изображение')
    ratio = IntegerField('Оценка', validators=[InputRequired()])
    submit = SubmitField('Добавить')

