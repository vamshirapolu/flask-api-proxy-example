import awsgi
from flask import (Flask, jsonify, Blueprint, send_from_directory, render_template, request)
import json
import os 

app = Flask(__name__, template_folder='docs/templates')

fields = {
    'base_url': 'dist',
    'app_name': 'Realtime Ingestion API',
    'config_json': json.dumps({
        'app_name': 'Realtime Ingestion API',
        'dom_id': '#realtime-ingestion-api',
        'url': 'https://bmngw78kr4.execute-api.us-east-1.amazonaws.com/dev/docs/swagger.json',
        'layout': 'StandaloneLayout'
    })
}

print(__file__)
base_path = os.path.dirname(os.path.realpath(__file__))
print('base_path {}'.format(base_path))

@app.route('/', methods=['GET'])
def index():
    return jsonify(status=200, message='OK')


@app.route('/docs')
@app.route('/docs/<path:path>')
def show(path=None):
    print('path: {}'.format(path))
    if not path or path == 'index.html':
        return render_template('index.template.html', **fields)
    else:
        print('Rendering {} from directory {}.'.format(path, os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs')))
        return send_from_directory(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                'docs'
            ),
            path
        )

@app.route('/greet/<path:user>', methods=['GET'])
def greetings(user):    
    return jsonify(status=200, message='Hello {}!'.format(user))


@app.route('/greetuser', methods=['GET'])
def greetingsByRequestParam():
    print(request.args)
    user = request.args.get('user')
    return jsonify(status=200, message='Hello {}!'.format(user))


def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)

