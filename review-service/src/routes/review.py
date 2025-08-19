from flask import Blueprint, request, jsonify
from flasgger import swag_from
from src.models.review import Review, ReviewHelpfulVote, db
from datetime import datetime, date
import requests
import os

review_bp = Blueprint('review', __name__)

# URLs dos outros serviços (podem ser configuradas via variáveis de ambiente)
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://localhost:3001')
EXPERIENCE_SERVICE_URL = os.getenv('EXPERIENCE_SERVICE_URL', 'http://localhost:3002')

def get_user_info(user_id):
    """Busca informações do usuário no User Service"""
    try:
        response = requests.get(f"{USER_SERVICE_URL}/api/users/{user_id}", timeout=5)
        if response.status_code == 200:
            return response.json().get('user')
    except:
        pass
    return None

def get_experience_info(experience_id):
    """Busca informações da experiência no Experience Service"""
    try:
        response = requests.get(f"{EXPERIENCE_SERVICE_URL}/api/experiences/{experience_id}", timeout=5)
        if response.status_code == 200:
            return response.json().get('experience')
    except:
        pass
    return None

@review_bp.route('/reviews', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Listar reviews',
    'parameters': [
        {'name': 'page', 'in': 'query', 'type': 'integer', 'description': 'Número da página'},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'description': 'Itens por página'},
        {'name': 'experience_id', 'in': 'query', 'type': 'string', 'description': 'Filtrar por experiência'},
        {'name': 'user_id', 'in': 'query', 'type': 'string', 'description': 'Filtrar por usuário'},
        {'name': 'min_rating', 'in': 'query', 'type': 'integer', 'description': 'Rating mínimo'},
        {'name': 'max_rating', 'in': 'query', 'type': 'integer', 'description': 'Rating máximo'},
        {'name': 'include_user_info', 'in': 'query', 'type': 'boolean', 'description': 'Incluir dados do usuário'}
    ],
    'responses': {
        200: {'description': 'Lista de reviews'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def get_reviews():
    """Lista reviews com filtros opcionais"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)
        
        # Filtros
        experience_id = request.args.get('experience_id')
        user_id = request.args.get('user_id')
        min_rating = request.args.get('min_rating', type=int)
        max_rating = request.args.get('max_rating', type=int)
        is_verified = request.args.get('is_verified', type=bool)
        include_user_info = request.args.get('include_user_info', False, type=bool)
        
        # Construir query
        query = Review.query
        
        # Aplicar filtros
        if experience_id:
            query = query.filter(Review.experience_id == experience_id)
        
        if user_id:
            query = query.filter(Review.user_id == user_id)
        
        if min_rating:
            query = query.filter(Review.rating >= min_rating)
        
        if max_rating:
            query = query.filter(Review.rating <= max_rating)
        
        if is_verified is not None:
            query = query.filter(Review.is_verified == is_verified)
        
        # Ordenação
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by == 'rating':
            if sort_order == 'asc':
                query = query.order_by(Review.rating.asc())
            else:
                query = query.order_by(Review.rating.desc())
        elif sort_by == 'helpful_votes':
            if sort_order == 'asc':
                query = query.order_by(Review.helpful_votes.asc())
            else:
                query = query.order_by(Review.helpful_votes.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(Review.created_at.asc())
            else:
                query = query.order_by(Review.created_at.desc())
        
        # Paginar
        reviews = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Preparar dados das reviews
        reviews_data = []
        for review in reviews.items:
            user_info = None
            if include_user_info:
                user_info = get_user_info(review.user_id)
            
            reviews_data.append(review.to_dict(
                include_user_info=include_user_info,
                user_info=user_info
            ))
        
        return jsonify({
            'reviews': reviews_data,
            'pagination': {
                'page': reviews.page,
                'pages': reviews.pages,
                'per_page': reviews.per_page,
                'total': reviews.total,
                'has_next': reviews.has_next,
                'has_prev': reviews.has_prev
            },
            'filters': {
                'experience_id': experience_id,
                'user_id': user_id,
                'min_rating': min_rating,
                'max_rating': max_rating,
                'is_verified': is_verified,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/reviews/<review_id>', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Obter review por ID',
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'string', 'required': True},
        {'name': 'include_user_info', 'in': 'query', 'type': 'boolean', 'description': 'Incluir dados do usuário'}
    ],
    'responses': {
        200: {'description': 'Dados do review'},
        404: {'description': 'Review não encontrada'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def get_review(review_id):
    """Busca uma review específica"""
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review não encontrada'}), 404
        
        include_user_info = request.args.get('include_user_info', False, type=bool)
        user_info = None
        
        if include_user_info:
            user_info = get_user_info(review.user_id)
        
        return jsonify({
            'review': review.to_dict(
                include_user_info=include_user_info,
                user_info=user_info
            )
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/reviews', methods=['POST'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Criar nova review',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'experience_id': {'type': 'string', 'description': 'ID da experiência'},
                    'user_id': {'type': 'string', 'description': 'ID do usuário'},
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5, 'description': 'Avaliação (1-5)'},
                    'title': {'type': 'string', 'description': 'Título da review'},
                    'content': {'type': 'string', 'description': 'Conteúdo da review'},
                    'photos': {'type': 'array', 'items': {'type': 'string'}, 'description': 'URLs das fotos'},
                    'visit_date': {'type': 'string', 'format': 'date', 'description': 'Data da visita (YYYY-MM-DD)'}
                },
                'required': ['experience_id', 'user_id', 'rating', 'content']
            }
        }
    ],
    'responses': {
        201: {'description': 'Review criada com sucesso'},
        400: {'description': 'Dados inválidos'},
        404: {'description': 'Experiência não encontrada'},
        409: {'description': 'Usuário já avaliou esta experiência'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def create_review():
    """Cria uma nova review"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['experience_id', 'user_id', 'rating', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar rating
        is_valid_rating, rating = Review.validate_rating(data['rating'])
        if not is_valid_rating:
            return jsonify({'error': 'Rating deve ser um número entre 1 e 5'}), 400
        
        # Verificar se usuário já avaliou esta experiência
        existing_review = Review.query.filter_by(
            experience_id=data['experience_id'],
            user_id=data['user_id']
        ).first()
        
        if existing_review:
            return jsonify({'error': 'Usuário já avaliou esta experiência'}), 409
        
        # Validar data de visita se fornecida
        visit_date = None
        if data.get('visit_date'):
            try:
                visit_date = datetime.strptime(data['visit_date'], '%Y-%m-%d').date()
                if visit_date > date.today():
                    return jsonify({'error': 'Data de visita não pode ser no futuro'}), 400
            except ValueError:
                return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        
        # Verificar se experiência existe (opcional, mas recomendado)
        # experience_info = get_experience_info(data['experience_id'])
        # if not experience_info:
        #     return jsonify({'error': 'Experiência não encontrada'}), 404
        
        # Calcular score de autenticidade
        authenticity_score = Review.calculate_authenticity_score(data)
        
        # Criar nova review
        review = Review(
            experience_id=data['experience_id'],
            user_id=data['user_id'],
            rating=rating,
            title=data.get('title', '').strip() if data.get('title') else None,
            content=data['content'].strip(),
            photos=data.get('photos', []),
            visit_date=visit_date,
            authenticity_score=authenticity_score
        )
        
        db.session.add(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review criada com sucesso',
            'review': review.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/reviews/<review_id>', methods=['PUT'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Atualizar review',
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'rating': {'type': 'integer', 'minimum': 1, 'maximum': 5},
                    'title': {'type': 'string'},
                    'content': {'type': 'string'},
                    'photos': {'type': 'array', 'items': {'type': 'string'}},
                    'visit_date': {'type': 'string', 'format': 'date'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Review atualizada com sucesso'},
        400: {'description': 'Dados inválidos'},
        404: {'description': 'Review não encontrada'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def update_review(review_id):
    """Atualiza uma review existente"""
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review não encontrada'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = ['rating', 'title', 'content', 'photos', 'visit_date']
        
        for field in updatable_fields:
            if field in data:
                if field == 'rating':
                    is_valid_rating, rating = Review.validate_rating(data[field])
                    if not is_valid_rating:
                        return jsonify({'error': 'Rating deve ser um número entre 1 e 5'}), 400
                    review.rating = rating
                elif field == 'visit_date':
                    if data[field]:
                        try:
                            visit_date = datetime.strptime(data[field], '%Y-%m-%d').date()
                            if visit_date > date.today():
                                return jsonify({'error': 'Data de visita não pode ser no futuro'}), 400
                            review.visit_date = visit_date
                        except ValueError:
                            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
                    else:
                        review.visit_date = None
                else:
                    setattr(review, field, data[field])
        
        # Recalcular score de autenticidade
        review.authenticity_score = Review.calculate_authenticity_score({
            'content': review.content,
            'photos': review.photos,
            'visit_date': review.visit_date.isoformat() if review.visit_date else None,
            'title': review.title
        })
        
        review.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Review atualizada com sucesso',
            'review': review.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/reviews/<review_id>', methods=['DELETE'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Deletar review',
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Review deletada com sucesso'},
        404: {'description': 'Review não encontrada'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def delete_review(review_id):
    """Deleta uma review"""
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review não encontrada'}), 404
        
        db.session.delete(review)
        db.session.commit()
        
        return jsonify({
            'message': 'Review deletada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/reviews/<review_id>/helpful', methods=['POST'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Votar review como útil',
    'parameters': [
        {'name': 'review_id', 'in': 'path', 'type': 'string', 'required': True},
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'string', 'description': 'ID do usuário'},
                    'is_helpful': {'type': 'boolean', 'description': 'Se a review é útil'}
                },
                'required': ['user_id', 'is_helpful']
            }
        }
    ],
    'responses': {
        200: {'description': 'Voto registrado com sucesso'},
        400: {'description': 'Dados inválidos'},
        404: {'description': 'Review não encontrada'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def vote_helpful(review_id):
    """Vota se uma review é útil ou não"""
    try:
        review = Review.query.get(review_id)
        
        if not review:
            return jsonify({'error': 'Review não encontrada'}), 404
        
        data = request.get_json()
        
        if 'user_id' not in data or 'is_helpful' not in data:
            return jsonify({'error': 'user_id e is_helpful são obrigatórios'}), 400
        
        # Verificar se usuário já votou nesta review
        existing_vote = ReviewHelpfulVote.query.filter_by(
            review_id=review_id,
            user_id=data['user_id']
        ).first()
        
        if existing_vote:
            # Atualizar voto existente
            existing_vote.is_helpful = data['is_helpful']
        else:
            # Criar novo voto
            vote = ReviewHelpfulVote(
                review_id=review_id,
                user_id=data['user_id'],
                is_helpful=data['is_helpful']
            )
            db.session.add(vote)
        
        # Recalcular contagem de votos úteis
        helpful_count = ReviewHelpfulVote.query.filter_by(
            review_id=review_id,
            is_helpful=True
        ).count()
        
        review.helpful_votes = helpful_count
        db.session.commit()
        
        return jsonify({
            'message': 'Voto registrado com sucesso',
            'helpful_votes': helpful_count
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@review_bp.route('/experiences/<experience_id>/reviews/stats', methods=['GET'])
@swag_from({
    'tags': ['Reviews'],
    'summary': 'Obter estatísticas de reviews de uma experiência',
    'parameters': [
        {'name': 'experience_id', 'in': 'path', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Estatísticas dos reviews'},
        500: {'description': 'Erro interno do servidor'}
    }
})
def get_experience_review_stats(experience_id):
    """Retorna estatísticas das reviews de uma experiência"""
    try:
        reviews = Review.query.filter_by(experience_id=experience_id).all()
        
        if not reviews:
            return jsonify({
                'experience_id': experience_id,
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                'verified_reviews': 0,
                'average_authenticity_score': 0.0
            }), 200
        
        # Calcular estatísticas
        total_reviews = len(reviews)
        total_rating = sum(review.rating for review in reviews)
        average_rating = total_rating / total_reviews
        
        # Distribuição de ratings
        rating_distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            rating_distribution[review.rating] += 1
        
        # Reviews verificadas
        verified_reviews = sum(1 for review in reviews if review.is_verified)
        
        # Score médio de autenticidade
        total_authenticity = sum(review.authenticity_score or 0 for review in reviews)
        average_authenticity = total_authenticity / total_reviews
        
        return jsonify({
            'experience_id': experience_id,
            'total_reviews': total_reviews,
            'average_rating': round(average_rating, 2),
            'rating_distribution': rating_distribution,
            'verified_reviews': verified_reviews,
            'average_authenticity_score': round(average_authenticity, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

