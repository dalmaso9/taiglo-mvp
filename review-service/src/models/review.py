from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import uuid

db = SQLAlchemy()

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experience_id = db.Column(db.String(36), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    photos = db.Column(db.JSON, default=[])  # Array de URLs das fotos
    visit_date = db.Column(db.Date)
    is_verified = db.Column(db.Boolean, default=False)
    authenticity_score = db.Column(db.Float, default=0.0)
    helpful_votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint única para evitar múltiplas avaliações do mesmo usuário para a mesma experiência
    __table_args__ = (
        db.UniqueConstraint('experience_id', 'user_id', name='unique_user_experience_review'),
    )
    
    def to_dict(self, include_user_info=False, user_info=None):
        review_dict = {
            'id': self.id,
            'experience_id': self.experience_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'title': self.title,
            'content': self.content,
            'photos': self.photos,
            'visit_date': self.visit_date.isoformat() if self.visit_date else None,
            'is_verified': self.is_verified,
            'authenticity_score': round(self.authenticity_score, 2) if self.authenticity_score else 0.0,
            'helpful_votes': self.helpful_votes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # Incluir informações do usuário se fornecidas
        if include_user_info and user_info:
            review_dict['user'] = user_info
            
        return review_dict
    
    @staticmethod
    def validate_rating(rating):
        """Valida se o rating está no intervalo correto"""
        try:
            rating = int(rating)
            return 1 <= rating <= 5, rating
        except (ValueError, TypeError):
            return False, None
    
    @staticmethod
    def calculate_authenticity_score(review_data):
        """Calcula um score de autenticidade básico para a review"""
        score = 0.0
        
        # Fatores que aumentam a autenticidade
        if review_data.get('content') and len(review_data['content']) > 50:
            score += 0.3  # Review detalhada
        
        if review_data.get('photos') and len(review_data['photos']) > 0:
            score += 0.2  # Tem fotos
        
        if review_data.get('visit_date'):
            try:
                visit_date = datetime.strptime(review_data['visit_date'], '%Y-%m-%d').date()
                days_ago = (date.today() - visit_date).days
                if days_ago <= 30:
                    score += 0.3  # Visita recente
                elif days_ago <= 90:
                    score += 0.2  # Visita relativamente recente
            except:
                pass
        
        if review_data.get('title') and len(review_data['title']) > 10:
            score += 0.2  # Título descritivo
        
        # Normalizar score entre 0 e 1
        return min(score, 1.0)
    
    def __repr__(self):
        return f'<Review {self.id} - Rating: {self.rating}>'

class ReviewHelpfulVote(db.Model):
    """Tabela para rastrear votos úteis nas reviews"""
    __tablename__ = 'review_helpful_votes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = db.Column(db.String(36), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    is_helpful = db.Column(db.Boolean, nullable=False)  # True = útil, False = não útil
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint única para evitar múltiplos votos do mesmo usuário na mesma review
    __table_args__ = (
        db.UniqueConstraint('review_id', 'user_id', name='unique_user_review_vote'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'review_id': self.review_id,
            'user_id': self.user_id,
            'is_helpful': self.is_helpful,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ReviewHelpfulVote {self.id} - Helpful: {self.is_helpful}>'

