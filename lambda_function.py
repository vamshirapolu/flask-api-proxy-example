import awsgi
from flask import (
    Flask,
    jsonify, 
    request
)
from flask_swagger import swagger

app = Flask(__name__)

app.run()

@app.route('/', methods=['GET'])
def index():
    return jsonify(status=200, message='OK')


@app.route('/greet/<path:user>', methods=['GET'])
def greetings(user):    
    return jsonify(status=200, message='Hello {}!'.format(user))


@app.route('/greetuser', methods=['GET'])
def greetingsByRequestParam():
    print(request.args)
    user = request.args.get('user')
    return jsonify(status=200, message='Hello {}!'.format(user))


@app.route("/api-doc")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "My API"
    return jsonify(swag)

def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)
