import awsgi
from flask import (
    Flask,
    jsonify,
)

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify(status=200, message='OK')


@app.route('/greet/<path:user>')
def greetings(user):    
    return jsonify(status=200, message='Hello {}!'.format(user))

def lambda_handler(event, context):
    return awsgi.response(app, event, context)
