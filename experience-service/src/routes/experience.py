from flask import Blueprint, request, jsonify
from src.models.experience import Experience, ExperienceCategory, db
from datetime import datetime
import uuid

experience_bp = Blueprint('experience', __name__)

@experience_bp.route('/experiences', methods=['GET'])
def get_experiences():
    """Lista todas as experiências com filtros opcionais"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Limitar para evitar sobrecarga
        
        # Filtros
        category_id = request.args.get('category_id')
        is_hidden_gem = request.args.get('is_hidden_gem', type=bool)
        min_rating = request.args.get('min_rating', type=float)
        price_range = request.args.get('price_range', type=int)
        search = request.args.get('search', '').strip()
        
        # Construir query
        query = Experience.query
        
        # Aplicar filtros
        if category_id:
            query = query.filter(Experience.category_id == category_id)
        
        if is_hidden_gem is not None:
            query = query.filter(Experience.is_hidden_gem == is_hidden_gem)
        
        if min_rating:
            query = query.filter(Experience.average_rating >= min_rating)
        
        if price_range:
            query = query.filter(Experience.price_range == price_range)
        
        if search:
            query = query.filter(
                db.or_(
                    Experience.name.ilike(f'%{search}%'),
                    Experience.description.ilike(f'%{search}%'),
                    Experience.address.ilike(f'%{search}%')
                )
            )
        
        # Ordenação
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        if sort_by == 'rating':
            if sort_order == 'asc':
                query = query.order_by(Experience.average_rating.asc())
            else:
                query = query.order_by(Experience.average_rating.desc())
        elif sort_by == 'name':
            if sort_order == 'asc':
                query = query.order_by(Experience.name.asc())
            else:
                query = query.order_by(Experience.name.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(Experience.created_at.asc())
            else:
                query = query.order_by(Experience.created_at.desc())
        
        # Paginar
        experiences = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'experiences': [exp.to_dict() for exp in experiences.items],
            'pagination': {
                'page': experiences.page,
                'pages': experiences.pages,
                'per_page': experiences.per_page,
                'total': experiences.total,
                'has_next': experiences.has_next,
                'has_prev': experiences.has_prev
            },
            'filters': {
                'category_id': category_id,
                'is_hidden_gem': is_hidden_gem,
                'min_rating': min_rating,
                'price_range': price_range,
                'search': search,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/<experience_id>', methods=['GET'])
def get_experience(experience_id):
    """Busca uma experiência específica"""
    try:
        experience = Experience.query.get(experience_id)
        
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        return jsonify({
            'experience': experience.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/nearby', methods=['GET'])
def get_nearby_experiences():
    """Busca experiências próximas a uma coordenada"""
    try:
        # Parâmetros obrigatórios
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude e longitude são obrigatórias'}), 400
        
        # Parâmetros opcionais
        radius_km = request.args.get('radius_km', 5, type=float)
        limit = request.args.get('limit', 50, type=int)
        category_id = request.args.get('category_id')
        min_rating = request.args.get('min_rating', type=float)
        
        # Limitar valores para evitar sobrecarga
        radius_km = min(radius_km, 50)  # Máximo 50km
        limit = min(limit, 100)  # Máximo 100 resultados
        
        # Buscar experiências próximas
        nearby_results = Experience.find_nearby(latitude, longitude, radius_km, limit)
        
        # Aplicar filtros adicionais se necessário
        filtered_results = []
        for experience, distance in nearby_results:
            # Filtro por categoria
            if category_id and experience.category_id != category_id:
                continue
            
            # Filtro por rating mínimo
            if min_rating and experience.average_rating < min_rating:
                continue
            
            filtered_results.append((experience, distance))
        
        return jsonify({
            'experiences': [
                exp.to_dict(include_distance=True, distance=dist) 
                for exp, dist in filtered_results
            ],
            'search_params': {
                'latitude': latitude,
                'longitude': longitude,
                'radius_km': radius_km,
                'limit': limit,
                'category_id': category_id,
                'min_rating': min_rating
            },
            'total_found': len(filtered_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences', methods=['POST'])
def create_experience():
    """Cria uma nova experiência"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['name', 'description', 'address', 'latitude', 'longitude']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Validar coordenadas
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            
            if not (-90 <= latitude <= 90):
                return jsonify({'error': 'Latitude deve estar entre -90 e 90'}), 400
            
            if not (-180 <= longitude <= 180):
                return jsonify({'error': 'Longitude deve estar entre -180 e 180'}), 400
                
        except (ValueError, TypeError):
            return jsonify({'error': 'Latitude e longitude devem ser números válidos'}), 400
        
        # Validar categoria se fornecida
        if data.get('category_id'):
            category = ExperienceCategory.query.get(data['category_id'])
            if not category:
                return jsonify({'error': 'Categoria não encontrada'}), 404
        
        # Criar nova experiência
        experience = Experience(
            name=data['name'].strip(),
            description=data['description'].strip(),
            category_id=data.get('category_id'),
            address=data['address'].strip(),
            latitude=latitude,
            longitude=longitude,
            phone=data.get('phone', '').strip() if data.get('phone') else None,
            website_url=data.get('website_url', '').strip() if data.get('website_url') else None,
            instagram_handle=data.get('instagram_handle', '').strip() if data.get('instagram_handle') else None,
            opening_hours=data.get('opening_hours', {}),
            price_range=data.get('price_range'),
            is_hidden_gem=data.get('is_hidden_gem', False),
            created_by=data.get('created_by')  # ID do usuário que criou
        )
        
        db.session.add(experience)
        db.session.commit()
        
        return jsonify({
            'message': 'Experiência criada com sucesso',
            'experience': experience.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/<experience_id>', methods=['PUT'])
def update_experience(experience_id):
    """Atualiza uma experiência existente"""
    try:
        experience = Experience.query.get(experience_id)
        
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = [
            'name', 'description', 'category_id', 'address', 
            'latitude', 'longitude', 'phone', 'website_url', 
            'instagram_handle', 'opening_hours', 'price_range', 
            'is_hidden_gem', 'is_verified'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field in ['latitude', 'longitude']:
                    # Validar coordenadas
                    try:
                        value = float(data[field])
                        if field == 'latitude' and not (-90 <= value <= 90):
                            return jsonify({'error': 'Latitude deve estar entre -90 e 90'}), 400
                        if field == 'longitude' and not (-180 <= value <= 180):
                            return jsonify({'error': 'Longitude deve estar entre -180 e 180'}), 400
                        setattr(experience, field, value)
                    except (ValueError, TypeError):
                        return jsonify({'error': f'{field} deve ser um número válido'}), 400
                elif field == 'category_id' and data[field]:
                    # Validar categoria
                    category = ExperienceCategory.query.get(data[field])
                    if not category:
                        return jsonify({'error': 'Categoria não encontrada'}), 404
                    setattr(experience, field, data[field])
                else:
                    setattr(experience, field, data[field])
        
        experience.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Experiência atualizada com sucesso',
            'experience': experience.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/<experience_id>', methods=['DELETE'])
def delete_experience(experience_id):
    """Deleta uma experiência"""
    try:
        experience = Experience.query.get(experience_id)
        
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        db.session.delete(experience)
        db.session.commit()
        
        return jsonify({
            'message': 'Experiência deletada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

