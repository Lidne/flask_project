import flask

from . import db_session
from .games import Games

blueprint = flask.Blueprint(
    'news_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/news')
def get_news():
    db_sess = db_session.create_session()
    news = db_sess.query(Games).all()
    return flask.jsonify(
        {
            'news':
                [item.to_dict(only=('title', 'content', 'user.name'))
                 for item in news]
        }
    )


@blueprint.route('/api/news/<int:news_id>', methods=['GET'])
def get_one_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(Games).get(news_id)
    if not news:
        return flask.jsonify({'error': 'Not found'})
    return flask.jsonify(
        {
            'news': news.to_dict(only=(
                'title', 'content', 'user_id', 'is_private'))
        }
    )


@blueprint.route('/api/news_add', methods=['POST'])
def create_news():
    if not flask.request.json:
        return flask.jsonify({'error': 'Empty request'})
    elif not all(key in flask.request.json for key in
                 ['title', 'content', 'user_id', 'is_private']):
        return flask.jsonify({'error': 'Bad request'})
    db_sess = db_session.create_session()
    news = Games(
        job=flask.request.json['job'],
        team_leader=flask.request.json['team_leader'],
        user_id=flask.request.json[''],
        is_private=flask.request.json['is_private']
    )
    db_sess.add(news)
    db_sess.commit()
    return flask.jsonify({'success': 'OK'})


@blueprint.route('/api/news_del/<int:news_id>', methods=['DELETE'])
def delete_news(news_id):
    db_sess = db_session.create_session()
    news = db_sess.query(Games).get(news_id)
    if not news:
        return flask.jsonify({'error': 'Not found'})
    db_sess.delete(news)
    db_sess.commit()
    return flask.jsonify({'success': 'OK'})
