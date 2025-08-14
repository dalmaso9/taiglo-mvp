from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
from werkzeug.security import check_password_hash
from datetime import timedelta
import bcrypt
import re
import traceback

auth_bp = Blueprint('auth', __name__, url_prefix="/api/auth")

def validate_email(email):
    """Valida formato do email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Valida se a senha atende aos critérios mínimos"""
    if len(password) < 6:
        return False, "Senha deve ter pelo menos 6 caracteres"
    return True, ""

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra um novo usuário"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['email', 'password', 'first_name', 'last_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar email
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        
        # Validar senha
        is_valid, message = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': message}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar novo usuário
        user = User(
            email=data['email'].lower().strip(),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            bio=data.get('bio', '').strip() if data.get('bio') else None
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Criar token de acesso
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': user.to_dict(),
            'access_token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Autentica um usuário"""
    try:
        data = request.get_json()
        if not isinstance(data, dict):
            return jsonify({"error": "Payload JSON inválido"}), 400
        
        # Validar campos obrigatórios
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=data['email'].lower().strip()).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha incorretos'}), 401
        
        # Criar token de acesso
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'access_token': access_token
        }), 200
        
    except Exception as e:
        app.logger.error("Erro no login: %s", e)
        app.logger.error(traceback.format_exc())
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna informações do usuário atual"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh_token():
    """Renova o token de acesso"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Criar novo token
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(days=7)
        )
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

