from flask_restful import reqparse

parser_games = reqparse.RequestParser()
parser_games.add_argument('name', required=True)
parser_games.add_argument('price', required=True, type=int)
parser_games.add_argument('description', required=False)
parser_games.add_argument('release_date', required=False)
parser_games.add_argument('developers', required=False)
parser_games.add_argument('ratio', required=False, type=float)
parser_games.add_argument('is_selling', required=False, type=bool)
parser_games.add_argument('genre', required=True, type=int)
