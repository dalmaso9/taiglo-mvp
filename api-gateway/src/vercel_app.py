import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
from routes.gateway import gateway_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'taiglo-gateway-secret-key-2024'

# Configurar CORS
CORS(app, origins="*")

# Configurar Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Taiglo API Gateway",
        "description": "API Gateway para o sistema Taiglo",
        "version": "1.0.0",
        "contact": {
            "name": "Taiglo Team",
            "email": "support@taiglo.com"
        }
    },
    "host": "taiglo.vercel.app",
    "basePath": "/api",
    "schemes": ["https"],
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Registrar blueprints
app.register_blueprint(gateway_bp, url_prefix='/api')

@app.route('/health')
@swag_from({
    'responses': {
        200: {
            'description': 'Serviço saudável',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string'},
                    'service': {'type': 'string'}
                }
            }
        }
    }
})
def health_check():
    return {'status': 'healthy', 'service': 'api-gateway'}, 200

# Para compatibilidade com Vercel
if __name__ == '__main__':
    app.run()
