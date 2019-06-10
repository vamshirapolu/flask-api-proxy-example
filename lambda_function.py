import awsgi
from flask import (
    Flask,
    jsonify, 
    request
)
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

SWAGGER_URL = '/api/docs'
API_URL = 'swagger.json'

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Test application"
    },
    # oauth_config={ # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    # 'clientId': "your-client-id",
    # 'clientSecret': "your-client-secret-if-required",
    # 'realm': "your-realms",
    # 'appName': "your-app-name",
    # 'scopeSeparator': " ",
    # 'additionalQueryStringParams': {'test': "hello"}
    # }
)

# Register blueprint at URL
# (URL must match the one given to factory function above)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

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

def lambda_handler(event, context):
    print(event)
    return awsgi.response(app, event, context)
