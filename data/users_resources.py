import flask
import flask_restful
from data import db_session
from data.parser import parser
from data.users import User


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    users = session.query(User).get(user_id)
    if not users:
        flask.abort(404)


class UsersResource(flask_restful.Resource):
    """Класс ресурса пользователя"""

    def get(self, user_id):
        """Функция возвращает ответ на get запрос"""

        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return flask.jsonify({'user': user.to_dict(
            only=('id', 'nick', 'email', 'hashed_password', 'modified_date'))})

    def delete(self, user_id):
        """Функция удаляет запись в бд по delete запросу"""

        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return flask.jsonify({'success': 'OK'})


class UsersListResource(flask_restful.Resource):
    """Класс полного списка пользователей"""
    def get(self):
        """Функция возвращает ответ на get запрос"""

        session = db_session.create_session()
        users = session.query(User).all()
        return flask.jsonify({'users': [item.to_dict(
            only=('id', 'nick', 'email', 'hashed_password', 'modified_date')) for item in users]})

    def post(self):
        """Функция добавляет нового пользователя по post запросу"""

        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            nick=args['nick'],
            email=args['email'],
            hashed_password=args['hashed_password'],
            admin=args['admin']
        )
        session.add(user)
        session.commit()
        return flask.jsonify({'success': 'OK'})
