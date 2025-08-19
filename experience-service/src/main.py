import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flasgger import Swagger, swag_from
from src.models.experience import db
from src.routes.experience import experience_bp
from src.routes.category import category_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'taiglo-experience-secret-key-2024'

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
        "title": "Taiglo Experience Service",
        "description": "API para gerenciamento de experiências do sistema Taiglo",
        "version": "1.0.0",
        "contact": {
            "name": "Taiglo Team",
            "email": "support@taiglo.com"
        }
    },
    "host": "localhost:3002",
    "basePath": "/api",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Registrar blueprints
app.register_blueprint(experience_bp, url_prefix='/api')
app.register_blueprint(category_bp, url_prefix='/api')

# Configurar PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://taiglo_user:taiglo_password@localhost:5432/taiglo_db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

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
    return {'status': 'healthy', 'service': 'experience-service'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)

