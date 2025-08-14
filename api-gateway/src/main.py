import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.routes.gateway import gateway_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'taiglo-gateway-secret-key-2024'

# Configurar CORS
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(gateway_bp, url_prefix='/api')

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
def health_check():
    return {'status': 'healthy', 'service': 'api-gateway'}, 200

@app.route('/services/health')
def services_health_check():
    """Verifica o status de todos os serviços"""
    import requests
    
    services = {
        'user-service': 'http://user-service:3001/health',
        'experience-service': 'http://experience-service:3002/health',
        'review-service': 'http://review-service:3004/health'
    }
    
    status = {}
    for service_name, url in services.items():
        try:
            response = requests.get(url, timeout=5)
            status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            status[service_name] = {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    all_healthy = all(s['status'] == 'healthy' for s in status.values())
    
    return {
        'gateway_status': 'healthy',
        'services': status,
        'overall_status': 'healthy' if all_healthy else 'degraded'
    }, 200 if all_healthy else 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

