from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

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
    
    def check_password(self, password):
        """Verifica se a senha fornecida está correta"""
        return check_password_hash(self.password_hash, password)
    
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
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            user_dict['password_hash'] = self.password_hash
            
        return user_dict
    
    def __repr__(self):
        return f'<User {self.email}>'

