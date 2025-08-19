from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    date_of_birth = db.Column(db.Date)
    profile_picture_url = db.Column(db.Text)
    bio = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    is_local_guide = db.Column(db.Boolean, default=False)
    preferences = db.Column(db.JSON, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """Hash e armazena a senha do usuário"""
        self.password_hash = generate_password_hash(password)
   
    def check_password(self, password: str) -> bool:
        """Verifica senha suportando bcrypt ($2b$...) e hashes do Werkzeug (scrypt/pbkdf2)"""
        h = (self.password_hash or "").strip()
        try:
            # bcrypt gerado externamente (ex.: seed.sql) começa com $2b$ (ou $2a$)
            if h.startswith("$2b$") or h.startswith("$2a$"):
                return bcrypt.checkpw(password.encode("utf-8"), h.encode("utf-8"))
            # hashes do Werkzeug: "method$salt$hash" (scrypt/pbkdf2)
            return check_password_hash(h, password)
        except Exception:
            # nunca deixe estourar aqui — credencial errada retorna False
            return False

    def has_permission(self, permission_name):
        """Verifica se o usuário tem uma permissão específica"""
        try:
            # Usar função do banco de dados para verificar permissão
            result = db.session.execute(
                'SELECT user_has_permission(:user_id, :permission)',
                {'user_id': self.id, 'permission': permission_name}
            ).scalar()
            return bool(result)
        except Exception:
            return False

    def has_role(self, role_name):
        """Verifica se o usuário tem um role específico"""
        try:
            result = db.session.execute(
                'SELECT COUNT(*) FROM user_roles ur JOIN roles r ON ur.role_id = r.id WHERE ur.user_id = :user_id AND r.name = :role_name AND r.is_active = TRUE',
                {'user_id': self.id, 'role_name': role_name}
            ).scalar()
            return result > 0
        except Exception:
            return False

    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.has_role('admin')

    def is_moderator(self):
        """Verifica se o usuário é moderador"""
        return self.has_role('moderator') or self.has_role('admin')

    def get_roles(self):
        """Retorna todos os roles do usuário"""
        try:
            result = db.session.execute(
                'SELECT role_name, role_description FROM get_user_roles(:user_id)',
                {'user_id': self.id}
            ).fetchall()
            return [{'name': row[0], 'description': row[1]} for row in result]
        except Exception:
            return []

    def get_permissions(self):
        """Retorna todas as permissões do usuário"""
        try:
            result = db.session.execute(
                'SELECT permission_name, resource, action FROM get_user_permissions(:user_id)',
                {'user_id': self.id}
            ).fetchall()
            return [{'name': row[0], 'resource': row[1], 'action': row[2]} for row in result]
        except Exception:
            return []

    def add_role(self, role_name):
        """Adiciona um role ao usuário"""
        try:
            # Buscar o role
            role = db.session.execute(
                'SELECT id FROM roles WHERE name = :role_name AND is_active = TRUE',
                {'role_name': role_name}
            ).scalar()
            
            if role:
                # Verificar se já tem o role
                existing = db.session.execute(
                    'SELECT id FROM user_roles WHERE user_id = :user_id AND role_id = :role_id',
                    {'user_id': self.id, 'role_id': role}
                ).scalar()
                
                if not existing:
                    db.session.execute(
                        'INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)',
                        {'user_id': self.id, 'role_id': role}
                    )
                    db.session.commit()
                    return True
            return False
        except Exception:
            db.session.rollback()
            return False

    def remove_role(self, role_name):
        """Remove um role do usuário"""
        try:
            result = db.session.execute(
                'DELETE FROM user_roles WHERE user_id = :user_id AND role_id = (SELECT id FROM roles WHERE name = :role_name)',
                {'user_id': self.id, 'role_name': role_name}
            )
            db.session.commit()
            return result.rowcount > 0
        except Exception:
            db.session.rollback()
            return False

    def to_dict(self, include_sensitive=False):
        """Converte o usuário para dicionário"""
        user_dict = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'profile_picture_url': self.profile_picture_url,
            'bio': self.bio,
            'is_verified': self.is_verified,
            'is_local_guide': self.is_local_guide,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'roles': self.get_roles(),
            'permissions': self.get_permissions()
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            
        return user_dict
    
    def __repr__(self):
        return f'<User {self.email}>'

