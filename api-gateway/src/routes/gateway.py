from flask import Blueprint, request, jsonify
from flasgger import swag_from
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
            'params': request.args
        }
        
        # Lidar com headers (remover alguns que podem causar problemas)
        headers = dict(request.headers)
        # Remover headers que podem causar problemas no proxy
        headers_to_remove = ['Content-Length', 'Host', 'Content-Type']
        for header in headers_to_remove:
            headers.pop(header, None)
        kwargs['headers'] = headers
        
        # Adicionar dados do corpo se necessário
        if request.files:
            # Upload de arquivos
            kwargs['files'] = request.files
            if request.form:
                kwargs['data'] = request.form
        elif request.is_json:
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
        return jsonify({'error': f'Erro interno do gateway: {str(e)}'}), 500

# Rotas do User Service
@gateway_bp.route('/auth/register', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Registrar novo usuário',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Usuário criado com sucesso'},
        400: {'description': 'Dados inválidos'},
        409: {'description': 'Usuário já existe'}
    }
})
def auth_register():
    return proxy_request(SERVICES['user'], '/api/auth/register', 'POST')

@gateway_bp.route('/auth/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Fazer login',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Login realizado com sucesso'},
        401: {'description': 'Credenciais inválidas'}
    }
})
def auth_login():
    return proxy_request(SERVICES['user'], '/api/auth/login', 'POST')

@gateway_bp.route('/auth/me', methods=['GET'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Obter dados do usuário logado',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Dados do usuário'},
        401: {'description': 'Token inválido'}
    }
})
def auth_me():
    return proxy_request(SERVICES['user'], '/api/auth/me', 'GET')

@gateway_bp.route('/auth/refresh', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Renovar token de acesso',
    'responses': {
        200: {'description': 'Token renovado'},
        401: {'description': 'Token inválido'}
    }
})
def auth_refresh():
    return proxy_request(SERVICES['user'], '/api/auth/refresh', 'POST')

@gateway_bp.route('/users', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Listar usuários',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'description': 'Número da página'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'description': 'Itens por página'}
    ],
    'responses': {
        200: {'description': 'Lista de usuários'}
    }
})
def get_users():
    return proxy_request(SERVICES['user'], '/api/users', 'GET')

@gateway_bp.route('/users/<user_id>', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Obter usuário por ID',
    'parameters': [
        {'name': 'user_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Dados do usuário'},
        404: {'description': 'Usuário não encontrado'}
    }
})
def get_user(user_id):
    return proxy_request(SERVICES['user'], f'/api/users/{user_id}', 'GET')

@gateway_bp.route('/users/profile', methods=['PUT'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Atualizar perfil do usuário',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'username': {'type': 'string'},
                    'email': {'type': 'string'},
                    'bio': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Perfil atualizado'},
        401: {'description': 'Token inválido'},
        400: {'description': 'Dados inválidos'}
    }
})
def update_profile():
    return proxy_request(SERVICES['user'], '/api/users/profile', 'PUT')

@gateway_bp.route('/users/profile', methods=['DELETE'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Deletar perfil do usuário',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Perfil deletado'},
        401: {'description': 'Token inválido'}
    }
})
def delete_profile():
    return proxy_request(SERVICES['user'], '/api/users/profile', 'DELETE')

@gateway_bp.route('/users/search', methods=['GET'])
@swag_from({
    'tags': ['Users'],
    'summary': 'Buscar usuários',
    'parameters': [
        {'name': 'q', 'in': 'query', 'type': 'string', 'required': True, 'description': 'Termo de busca'}
    ],
    'responses': {
        200: {'description': 'Resultados da busca'}
    }
})
def search_users():
    return proxy_request(SERVICES['user'], '/api/users/search', 'GET')

# Rotas do Experience Service
@gateway_bp.route('/experiences', methods=['GET'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Listar experiências',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'description': 'Número da página'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'description': 'Itens por página'},
        {'name': 'category', 'in': 'query', 'type': 'string', 'description': 'Filtrar por categoria'},
        {'name': 'search', 'in': 'query', 'type': 'string', 'description': 'Termo de busca'}
    ],
    'responses': {
        200: {'description': 'Lista de experiências'}
    }
})
def get_experiences():
    return proxy_request(SERVICES['experience'], '/api/experiences', 'GET')

@gateway_bp.route('/experiences/<experience_id>', methods=['GET'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Obter experiência por ID',
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Dados da experiência'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def get_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'GET')

@gateway_bp.route('/experiences/nearby', methods=['GET'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Buscar experiências próximas',
    'parameters': [
        {'name': 'lat', 'in': 'query', 'type': 'number', 'required': True, 'description': 'Latitude'},
        {'name': 'lng', 'in': 'query', 'type': 'number', 'required': True, 'description': 'Longitude'},
        {'name': 'radius', 'in': 'query', 'type': 'number', 'description': 'Raio em km (padrão: 10)'}
    ],
    'responses': {
        200: {'description': 'Experiências próximas'}
    }
})
def get_nearby_experiences():
    return proxy_request(SERVICES['experience'], '/api/experiences/nearby', 'GET')

@gateway_bp.route('/experiences', methods=['POST'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Criar nova experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'category_id': {'type': 'integer'},
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'},
                    'address': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Experiência criada'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'}
    }
})
def create_experience():
    return proxy_request(SERVICES['experience'], '/api/experiences', 'POST')

@gateway_bp.route('/experiences/<experience_id>', methods=['PUT'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Atualizar experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'description': {'type': 'string'},
                    'category_id': {'type': 'integer'},
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'},
                    'address': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Experiência atualizada'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def update_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'PUT')

@gateway_bp.route('/experiences/<experience_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Deletar experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Experiência deletada'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def delete_experience(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}', 'DELETE')

# Rotas de Fotos para Experiências
@gateway_bp.route('/experiences/<experience_id>/photos', methods=['POST'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Upload de fotos para experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'photos', 'in': 'formData', 'type': 'file', 'required': True, 'multiple': True}
    ],
    'responses': {
        200: {'description': 'Fotos enviadas com sucesso'},
        400: {'description': 'Arquivo inválido'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def upload_experience_photos(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}/photos', 'POST')

@gateway_bp.route('/experiences/<experience_id>/photos', methods=['DELETE'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Remover fotos de experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'photo_urls': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Fotos removidas com sucesso'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def delete_experience_photos(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}/photos', 'DELETE')

@gateway_bp.route('/experiences/<experience_id>/photos/reorder', methods=['PUT'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Reordenar fotos de experiência',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'photo_order': {
                        'type': 'array',
                        'items': {'type': 'string'}
                    }
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Fotos reordenadas com sucesso'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def reorder_experience_photos(experience_id):
    return proxy_request(SERVICES['experience'], f'/api/experiences/{experience_id}/photos/reorder', 'PUT')

# Rotas do Review Service
@gateway_bp.route('/reviews', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Listar reviews',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'description': 'Número da página'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'description': 'Itens por página'},
        {'name': 'experience_id', 'in': 'query', 'type': 'integer', 'description': 'Filtrar por experiência'},
        {'name': 'user_id', 'in': 'query', 'type': 'integer', 'description': 'Filtrar por usuário'}
    ],
    'responses': {
        200: {'description': 'Lista de reviews'}
    }
})
def get_reviews():
    return proxy_request(SERVICES['review'], '/api/reviews', 'GET')

@gateway_bp.route('/reviews/<review_id>', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Obter review por ID',
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Dados do review'},
        404: {'description': 'Review não encontrado'}
    }
})
def get_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'GET')

@gateway_bp.route('/reviews', methods=['POST'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Criar novo review',
    'security': [{'Bearer': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'experience_id': {'type': 'integer'},
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comment': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        201: {'description': 'Review criado'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'}
    }
})
def create_review():
    return proxy_request(SERVICES['review'], '/api/reviews', 'POST')

@gateway_bp.route('/reviews/<review_id>', methods=['PUT'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Atualizar review',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'integer', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'comment': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Review atualizado'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Review não encontrado'}
    }
})
def update_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'PUT')

@gateway_bp.route('/reviews/<review_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Deletar review',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Review deletado'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Review não encontrado'}
    }
})
def delete_review(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}', 'DELETE')

@gateway_bp.route('/reviews/<review_id>/helpful', methods=['POST'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Votar review como útil',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Voto registrado'},
        401: {'description': 'Token inválido'},
        404: {'description': 'Review não encontrado'}
    }
})
def vote_helpful(review_id):
    return proxy_request(SERVICES['review'], f'/api/reviews/{review_id}/helpful', 'POST')

@gateway_bp.route('/experiences/<experience_id>/reviews/stats', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Obter estatísticas de reviews de uma experiência',
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Estatísticas dos reviews'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def get_experience_review_stats(experience_id):
    return proxy_request(SERVICES['review'], f'/api/experiences/{experience_id}/reviews/stats', 'GET')

# Rotas combinadas (que fazem chamadas para múltiplos serviços)
@gateway_bp.route('/experiences/<experience_id>/full', methods=['GET'])
@swag_from({
    'tags': ['Experiences'],
    'summary': 'Obter experiência completa com reviews e estatísticas',
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Experiência completa'},
        404: {'description': 'Experiência não encontrada'},
        500: {'description': 'Erro interno'}
    }
})
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
@swag_from({
    'tags': ['Search'],
    'summary': 'Busca unificada em experiências e reviews',
    'parameters': [
        {'name': 'q', 'in': 'query', 'type': 'string', 'required': True, 'description': 'Termo de busca'}
    ],
    'responses': {
        200: {'description': 'Resultados da busca'},
        400: {'description': 'Parâmetro de busca obrigatório'},
        500: {'description': 'Erro interno'}
    }
})
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

# ==================== ROTAS DE ADMIN ====================

@gateway_bp.route('/admin/experiences/bulk-upload', methods=['POST'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Upload em lote de experiências',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'file', 'in': 'formData', 'type': 'file', 'required': True}
    ],
    'responses': {
        201: {'description': 'Experiências criadas com sucesso'},
        400: {'description': 'Arquivo inválido'},
        401: {'description': 'Token inválido'}
    }
})
def admin_bulk_upload_experiences():
    """Upload em lote de experiências via planilha"""
    try:
        # Verificar se há arquivo
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Preparar dados para enviar ao experience-service
        files = {'file': (file.filename, file.stream, file.content_type)}
        headers = {'Authorization': request.headers.get('Authorization', '')}
        
        # Fazer requisição direta ao experience-service
        response = requests.post(
            f"{SERVICES['experience']}/api/admin/experiences/bulk-upload",
            files=files,
            headers=headers,
            timeout=120
        )
        
        return response.json(), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout na requisição'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Serviço indisponível'}), 503
    except Exception as e:
        return jsonify({'error': f'Erro interno do gateway: {str(e)}'}), 500

@gateway_bp.route('/admin/experiences/template', methods=['GET'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Obter template para upload de experiências',
    'security': [{'Bearer': []}],
    'responses': {
        200: {'description': 'Template de upload'},
        401: {'description': 'Token inválido'},
        403: {'description': 'Acesso negado - apenas admins'}
    }
})
def admin_get_upload_template():
    """Retorna template para upload de experiências"""
    return proxy_request(SERVICES['experience'], '/api/admin/experiences/template', 'GET')

@gateway_bp.route('/admin/experiences/<experience_id>', methods=['PUT'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Atualizar experiência (rota de admin)',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'},
                    'category_id': {'type': 'string'},
                    'address': {'type': 'string'},
                    'latitude': {'type': 'number'},
                    'longitude': {'type': 'number'},
                    'phone': {'type': 'string'},
                    'website_url': {'type': 'string'},
                    'instagram_handle': {'type': 'string'},
                    'opening_hours': {'type': 'object'},
                    'price_range': {'type': 'integer'},
                    'is_hidden_gem': {'type': 'boolean'},
                    'is_verified': {'type': 'boolean'},
                    'is_active': {'type': 'boolean'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Experiência atualizada'},
        400: {'description': 'Dados inválidos'},
        401: {'description': 'Token inválido'},
        403: {'description': 'Acesso negado - apenas admins'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def admin_update_experience(experience_id):
    """Atualiza uma experiência (rota de admin)"""
    return proxy_request(SERVICES['experience'], f'/api/admin/experiences/{experience_id}', 'PUT')

@gateway_bp.route('/admin/experiences/<experience_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Admin'],
    'summary': 'Deletar experiência (rota de admin)',
    'security': [{'Bearer': []}],
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Experiência deletada'},
        401: {'description': 'Token inválido'},
        403: {'description': 'Acesso negado - apenas admins'},
        404: {'description': 'Experiência não encontrada'}
    }
})
def admin_delete_experience(experience_id):
    """Deleta uma experiência (rota de admin)"""
    return proxy_request(SERVICES['experience'], f'/api/admin/experiences/{experience_id}', 'DELETE')

