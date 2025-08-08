from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from datetime import datetime

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    """Lista todos os usuários (para admin/debug)"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Limitar per_page para evitar sobrecarga
        per_page = min(per_page, 100)
        
        users = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Busca um usuário específico"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/users/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Atualiza o perfil do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = [
            'first_name', 'last_name', 'phone', 'bio', 
            'profile_picture_url', 'date_of_birth', 'preferences'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'date_of_birth' and data[field]:
                    # Converter string para date
                    try:
                        user.date_of_birth = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
                else:
                    setattr(user, field, data[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/users/profile', methods=['DELETE'])
@jwt_required()
def delete_profile():
    """Deleta a conta do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'message': 'Conta deletada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@user_bp.route('/users/search', methods=['GET'])
def search_users():
    """Busca usuários por nome ou email"""
    try:
        query = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if not query:
            return jsonify({'error': 'Parâmetro de busca é obrigatório'}), 400
        
        # Limitar per_page
        per_page = min(per_page, 100)
        
        # Buscar por nome ou email
        users = User.query.filter(
            db.or_(
                User.first_name.ilike(f'%{query}%'),
                User.last_name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%')
            )
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            },
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

