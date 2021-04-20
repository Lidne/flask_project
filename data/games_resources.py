import flask
import flask_restful
from data import db_session
from data.parser_games import parser_games
from data.games import Game


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    games = session.query(Game).get(user_id)
    if not games:
        flask.abort(404)


class GamesResource(flask_restful.Resource):
    """Класс ресурса игры"""

    def get(self, game_id):
        """Функция возвращает ответ на get запрос"""
        abort_if_user_not_found(game_id)
        session = db_session.create_session()
        user = session.query(Game).get(game_id)
        return flask.jsonify({'game': user.to_dict(
            only=('id', 'name', 'price', 'description', 'developers', 'release_date',
                  'ratio', 'is_selling', 'genre', 'img', 'img_wide'))})

    def delete(self, game_id):
        """Функция удаляет запись в бд по delete запросу"""
        abort_if_user_not_found(game_id)
        session = db_session.create_session()
        game = session.query(Game).get(game_id)
        session.delete(game)
        session.commit()
        return flask.jsonify({'success': 'OK'})


class GamesListResource(flask_restful.Resource):
    """Класс полного списка игр"""

    def get(self):
        """Функция возвращает ответ на get запрос"""
        session = db_session.create_session()
        games = session.query(Game).all()
        return flask.jsonify({'games': [item.to_dict(
            only=(
                'id', 'name', 'price', 'description', 'developers',
                'release_date', 'ratio', 'is_selling', 'genre', 'img', 'img_wide'
            )) for item in games]})

    def post(self):
        """Функция добавляет нового пользователя по post запросу"""
        args = parser_games.parse_args()
        print(args)
        session = db_session.create_session()
        game = Game(
            price=args['price'],
            name=args['name'],
            description=args['description'],
            developers=args['developers'],
            release_date=args['release_date'],
            ratio=args['ratio'],
            is_selling=args['is_selling'],
            genre=args['genre'],
            img=args['img'],
            img_wide=args['img_wide']
        )
        session.add(game)
        session.commit()
        return flask.jsonify({'success': 'OK'})
