import awsgi
from flask import (
    Flask,
    jsonify, 
    request,
    Blueprint
)
from flask_restplus import Api


app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/')
api = Api(blueprint, doc='/api-doc/')

app.register_blueprint(blueprint)

@api.route('/', methods=['GET'])
def index():
    return jsonify(status=200, message='OK')


@api.route('/greet/<path:user>', endpoint='greet', methods=['GET'])
def greetings(user):    
    return jsonify(status=200, message='Hello {}!'.format(user))


@api.route('/greetuser', endpoint='greet_user', methods=['GET'])
def greetingsByRequestParam():
    print(request.args)
    user = request.args.get('user')
    return jsonify(status=200, message='Hello {}!'.format(user))

def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)
