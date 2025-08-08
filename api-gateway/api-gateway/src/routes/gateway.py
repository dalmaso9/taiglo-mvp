from flask import Blueprint, request, jsonify
import requests
import os

gateway_bp = Blueprint('gateway', __name__)

# URLs dos serviços
SERVICES = {
    'user': os.getenv('USER_SERVICE_URL', 'http://localhost:3001'),
    'experience': os.getenv('EXPERIENCE_SERVICE_URL', 'http://localhost:3002'),
    'review': os.getenv('REVIEW_SERVICE_URL', 'http://localhost:3004')
}

def proxy_request(service_url, path, method='GET', timeout=30):
    """Função auxiliar para fazer proxy das requisições"""
    try:
        url = f"{service_url}{path}"
        
        # Preparar dados da requisição
        kwargs = {
            'timeout': timeout,
            'headers': dict(request.headers),
            'params': request.args
        }
        
        # Adicionar dados do corpo se necessário
        if request.is_json:
            kwargs['json'] = request.get_json()
        elif request.data:
            kwargs['data'] = request.data
            
        # Fazer a requisição
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)
        else:
            return jsonify({'error': 'Método não suportado'}), 405
        
        # Retornar resposta
        try:
            return response.json(), response.status_code
        except:
            return {'message': response.text}, response.status_code
            
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout na requisição'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Serviço indisponível'}), 503
    except Exception as e:
        return jsonify({'error': 'Erro interno do gateway'}), 500

# Rotas do User Service
@gateway_bp.route('/auth/register', methods=['POST'])
def auth_register():
    return proxy_request(SERVICES['user'], '/api/auth/register', 'POST')

@gateway_bp.route('/auth/login', methods=['POST'])
def auth_login():
    return proxy_request(SERVICES['user'], '/api/auth/login', 'POST')

@gateway_bp.route('/auth/me', methods=['GET'])
def auth_me():
    return proxy_request(SERVICES['user'], '/api/auth/me', 'GET')

@gateway_bp.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    return proxy_request(SERVICES['user'], '/api/auth/refresh', 'POST')

@gateway_bp.route('/users', methods=['GET'])
def get_users():
    return proxy_request(SERVICES['user'], '/api/users', 'GET')

@gateway_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    return proxy_request(SERVICES['user'], f'/api/users/{user_id}', 'GET')

@gateway_bp.route('/users/profile', methods=['PUT'])
def update_profile():
    return proxy_request(SERVICES['user'], '/api/users/profile', 'PUT')

@gateway_bp.route('/users/profile', methods=['DELETE'])
def delete_profile():
    return proxy_request(SERVICES['user'], '/api/users/profile', 'DELETE')

@gateway_bp.route('/users/search', methods=['GET'])
def search_users():
    return proxy_request(SERVICES['user'], '/api/users/search', 'GET')

# Rotas do Experience Service
@gateway_bp.route('/experiences', methods=['GET'])
def get_experiences():
    return proxy_request(SERVICES['experience'], '/api/experiences', 'GET')

@gateway_bp.route('/experiences/<experience_id>', methods=['GET'])
def get_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'GET')

@gateway_bp.route('/experiences/nearby', methods=['GET'])
def get_nearby_experiences():
    return proxy_request(SERVICES['experience'], '/api/experiences/nearby', 'GET')

@gateway_bp.route('/experiences', methods=['POST'])
def create_experience():
    return proxy_request(SERVICES['experience'], '/api/experiences', 'POST')

@gateway_bp.route('/experiences/<experience_id>', methods=['PUT'])
def update_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'PUT')

@gateway_bp.route('/experiences/<experience_id>', methods=['DELETE'])
def delete_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'DELETE')

@gateway_bp.route('/categories', methods=['GET'])
def get_categories():
    return proxy_request(SERVICES['experience'], '/api/categories', 'GET')

@gateway_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    return proxy_request(SERVICES['experience'], f'/api/categories/{category_id}', 'GET')

@gateway_bp.route('/categories', methods=['POST'])
def create_category():
    return proxy_request(SERVICES['experience'], '/api/categories', 'POST')

@gateway_bp.route('/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    return proxy_request(SERVICES['experience'], f'/api/categories/{category_id}', 'PUT')

@gateway_bp.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    return proxy_request(SERVICES['experience'], f'/api/categories/{category_id}', 'DELETE')

# Rotas do Review Service
@gateway_bp.route('/reviews', methods=['GET'])
def get_reviews():
    return proxy_request(SERVICES['review'], '/api/reviews', 'GET')

@gateway_bp.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'GET')

@gateway_bp.route('/reviews', methods=['POST'])
def create_review():
    return proxy_request(SERVICES['review'], '/api/reviews', 'POST')

@gateway_bp.route('/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'PUT')

@gateway_bp.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'DELETE')

@gateway_bp.route('/reviews/<review_id>/helpful', methods=['POST'])
def vote_helpful(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}/helpful', 'POST')

@gateway_bp.route('/experiences/<experience_id>/reviews/stats', methods=['GET'])
def get_experience_review_stats(experience_id):
    return proxy_request(SERVICES['review'], f'/api/experiences/{experience_id}/reviews/stats', 'GET')

# Rotas combinadas (que fazem chamadas para múltiplos serviços)
@gateway_bp.route('/experiences/<experience_id>/full', methods=['GET'])
def get_experience_full(experience_id):
    """Retorna experiência com reviews e estatísticas"""
    try:
        # Buscar experiência
        exp_response = requests.get(f"{SERVICES['experience']}/api/experiences/{experience_id}", timeout=10)
        if exp_response.status_code != 200:
            return exp_response.json(), exp_response.status_code
        
        experience_data = exp_response.json()
        
        # Buscar reviews da experiência
        reviews_response = requests.get(
            f"{SERVICES['review']}/api/reviews",
            params={'experience_id': experience_id, 'include_user_info': True},
            timeout=10
        )
        
        # Buscar estatísticas das reviews
        stats_response = requests.get(
            f"{SERVICES['review']}/api/experiences/{experience_id}/reviews/stats",
            timeout=10
        )
        
        # Combinar dados
        result = experience_data
        
        if reviews_response.status_code == 200:
            result['reviews'] = reviews_response.json().get('reviews', [])
        else:
            result['reviews'] = []
        
        if stats_response.status_code == 200:
            result['review_stats'] = stats_response.json()
        else:
            result['review_stats'] = {}
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro ao buscar dados completos da experiência'}), 500

@gateway_bp.route('/search', methods=['GET'])
def unified_search():
    """Busca unificada em experiências e reviews"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'Parâmetro de busca é obrigatório'}), 400
        
        # Buscar experiências
        exp_response = requests.get(
            f"{SERVICES['experience']}/api/experiences",
            params={'search': query},
            timeout=10
        )
        
        experiences = []
        if exp_response.status_code == 200:
            experiences = exp_response.json().get('experiences', [])
        
        return jsonify({
            'query': query,
            'experiences': experiences,
            'total_found': len(experiences)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro na busca unificada'}), 500

