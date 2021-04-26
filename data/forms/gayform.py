from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField, FileField, DateField
from wtforms.validators import DataRequired, Email, InputRequired


class GameForm(FlaskForm):
    name = StringField('Название', validators=[InputRequired()])
    price = IntegerField('Цена', validators=[InputRequired()])
    description = TextAreaField('Описание')
    developers = StringField('Разработчики', validators=[InputRequired()])
    release_date = StringField('Дата', validators=[InputRequired()])
    genre = StringField('Жанр', validators=[InputRequired()])
    img = FileField('Изображение')
    img_wide = FileField('Широкое изображение')
    ratio = IntegerField('Оценка', validators=[InputRequired()])
    submit = SubmitField('Post')

