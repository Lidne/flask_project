from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('nick', required=True)
parser.add_argument('email', required=True)
parser.add_argument('hashed_password', required=True)
parser.add_argument('admin', required=False, type=bool)
parser.add_argument('user_id', required=False, type=int)
