from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    nick = StringField('Имя', validators=[DataRequired()])
    email = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    remember_me = BooleanField('Не выходить')
    submit = SubmitField('Зарегестрироваться')
