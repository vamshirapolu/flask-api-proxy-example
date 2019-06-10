import awsgi
from flask import (Flask, jsonify, Blueprint, send_from_directory, render_template, request)
import json
import os 

app = Flask(__name__)

fields = {
    'base_url': 'docs',
    'app_name': 'Realtime Ingestion API',
    'config_json': json.dumps({
        'app_name': 'Realtime Ingestion API',
        'dom_id': '#realtime-ingestion-api',
        'url': 'https://bmngw78kr4.execute-api.us-east-1.amazonaws.com/dev/docs/swagger.json',
        'layout': 'StandaloneLayout'
    })
}

base_path = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET'])
def index():
    return jsonify(status=200, message='OK')


@swagger_ui.route('/docs')
@swagger_ui.route('/docs/<path:path>')
def show(path=None):
        if not path or path == 'index.html':
            return render_template('index.template.html', **fields)
        else:
            return send_from_directory(
                os.path.join(
                    base_path,
                    '/docs'
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


@app.route("/api-doc")
def spec():
    swag = swagger(app)
    swag['info']['version'] = "1.0"
    swag['info']['title'] = "My API"
    return jsonify(swag)

def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)

