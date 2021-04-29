from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, InputRequired, EqualTo


class LoginForm(FlaskForm):
    email = StringField('Логин', validators=[Email()])
    password = PasswordField('Пароль', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    remember_me = BooleanField('Не выходить')
    submit = SubmitField('Войти')
