from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import User, db
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def admin_required(fn):
    """Decorator para verificar se o usuário é admin"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin():
            return jsonify({'error': 'Acesso negado. Apenas administradores podem acessar este recurso.'}), 403
        
        return fn(*args, **kwargs)
    return wrapper

def permission_required(permission_name):
    """Decorator para verificar se o usuário tem uma permissão específica"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.has_permission(permission_name):
                return jsonify({'error': f'Acesso negado. Permissão "{permission_name}" é necessária.'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def role_required(role_name):
    """Decorator para verificar se o usuário tem um role específico"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.has_role(role_name):
                return jsonify({'error': f'Acesso negado. Role "{role_name}" é necessário.'}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

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
        
        # Verificar se email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 409
        
        # Criar novo usuário
        user = User(
            email=data['email'].lower().strip(),
            first_name=data['first_name'].strip(),
            last_name=data['last_name'].strip(),
            phone=data.get('phone', '').strip() if data.get('phone') else None
        )
        
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Adicionar role padrão 'user' se especificado
        if data.get('role'):
            user.add_role(data['role'])
        
        # Gerar token de acesso
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Faz login do usuário"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(email=data['email'].lower().strip()).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        # Gerar token de acesso
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Retorna dados do usuário logado"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Renova o token de acesso"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Gerar novo token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

# Rotas de administração de roles (apenas para admins)
@auth_bp.route('/users/<user_id>/roles', methods=['GET'])
@jwt_required()
@permission_required('users.admin')
def get_user_roles(user_id):
    """Retorna os roles de um usuário"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'user_id': user_id,
            'roles': user.get_roles(),
            'permissions': user.get_permissions()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/users/<user_id>/roles', methods=['POST'])
@jwt_required()
@permission_required('users.admin')
def add_user_role(user_id):
    """Adiciona um role a um usuário"""
    try:
        data = request.get_json()
        role_name = data.get('role')
        
        if not role_name:
            return jsonify({'error': 'Nome do role é obrigatório'}), 400
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.add_role(role_name):
            return jsonify({
                'message': f'Role "{role_name}" adicionado com sucesso',
                'roles': user.get_roles()
            }), 200
        else:
            return jsonify({'error': 'Erro ao adicionar role'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/users/<user_id>/roles/<role_name>', methods=['DELETE'])
@jwt_required()
@permission_required('users.admin')
def remove_user_role(user_id, role_name):
    """Remove um role de um usuário"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        if user.remove_role(role_name):
            return jsonify({
                'message': f'Role "{role_name}" removido com sucesso',
                'roles': user.get_roles()
            }), 200
        else:
            return jsonify({'error': 'Erro ao remover role'}), 400
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

