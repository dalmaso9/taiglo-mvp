from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func, text
import uuid
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement

db = SQLAlchemy()

class ExperienceCategory(db.Model):
    __tablename__ = 'experience_categories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    color_hex = db.Column(db.String(7), default='#000000')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com experiências
    experiences = db.relationship('Experience', backref='category', lazy=True)
    
    def to_dict(self):
        count = db.session.query(func.count(Experience.id))\
            .filter(Experience.category_id == self.id).scalar()
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon_url': self.icon_url,
            'color_hex': self.color_hex,
            'created_at': self.created_at.isoformat(),
            'experience_count': count
        }
    
    def __repr__(self):
        return f'<ExperienceCategory {self.name}>'

class Experience(db.Model):
    __tablename__ = 'experiences'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.String(36), db.ForeignKey('experience_categories.id'))
    address = db.Column(db.Text, nullable=False)
    
    # Coordenadas geográficas (lat, lng)
    location = db.Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    phone = db.Column(db.String(20))
    website_url = db.Column(db.Text)
    instagram_handle = db.Column(db.String(100))
    opening_hours = db.Column(db.JSON, default={})
    price_range = db.Column(db.Integer)  # 1-4 ($-$$$$)
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    is_hidden_gem = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    authenticity_score = db.Column(db.Float, default=0.0)
    photos = db.Column(db.JSON, default=[])  # Array de URLs das fotos
    created_by = db.Column(db.String(36))  # User ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self, include_distance=False, distance=None):
        # Extrai x=lon, y=lat do POINT
        lon = db.session.scalar(func.ST_X(self.location))
        lat = db.session.scalar(func.ST_Y(self.location))
        experience_dict = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id,
            'category': self.category.to_dict() if self.category else None,
            'address': self.address,
            'coordinates': {'latitude': lat, 'longitude': lon},
            'phone': self.phone,
            'website_url': self.website_url,
            'instagram_handle': self.instagram_handle,
            'opening_hours': self.opening_hours,
            'price_range': self.price_range,
            'average_rating': round(self.average_rating, 2) if self.average_rating else 0.0,
            'total_reviews': self.total_reviews,
            'is_hidden_gem': self.is_hidden_gem,
            'is_verified': self.is_verified,
            'authenticity_score': round(self.authenticity_score, 2) if self.authenticity_score else 0.0,
            'photos': self.photos,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
   
        if include_distance and distance is not None:
            experience_dict['distance_km'] = round(distance, 2)
            
        return experience_dict
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calcula a distância entre dois pontos usando a fórmula de Haversine"""
        from math import radians, cos, sin, asin, sqrt
        
        # Converter para radianos
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Fórmula de Haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        
        # Raio da Terra em km
        r = 6371
        
        return c * r
    
    @classmethod
    #def find_nearby(cls, latitude, longitude, radius_km=5, limit=50):
    #    """Encontra experiências próximas a uma coordenada"""
    #    experiences = cls.query.all()
    #    nearby_experiences = []
    #    
    #    for exp in experiences:
    #        distance = cls.calculate_distance(
    #            latitude, longitude,
    #            exp.latitude, exp.longitude
    #        )
            
    #        if distance <= radius_km:
    #            nearby_experiences.append((exp, distance))
        
        # Ordenar por distância
    #    nearby_experiences.sort(key=lambda x: x[1])
        
        # Limitar resultados
    #    return nearby_experiences[:limit]
    
    def __repr__(self):
        return f'<Experience {self.name}>'

