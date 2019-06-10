import awsgi
from flask import (
    Flask,
    jsonify, 
    request
)

app = Flask(__name__)

@app.route('/', method='GET')
def index():
    return jsonify(status=200, message='OK')


@app.route('/greet/<path:user>', method='GET')
def greetings(user):    
    return jsonify(status=200, message='Hello {}!'.format(user))

@app.route('/greet', method='GET')
def greetingsByRequestParam():
    print(request.args)
    user = request.args.get('user')
    return jsonify(status=200, message='Hello {}!'.format(user))

def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)
