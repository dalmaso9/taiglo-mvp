from flask import Blueprint, request, jsonify, current_app
from src.models.experience import Experience, ExperienceCategory, db
from datetime import datetime
import uuid
from geoalchemy2.elements import WKTElement
import pandas as pd
import io
import os
from werkzeug.utils import secure_filename
from PIL import Image
import base64

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

            # depois de validar latitude/longitude como float:
            point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
          
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
            location=point,
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
        current_app.logger.exception("create_experience failed")
        # Em desenvolvimento, retorne o erro para ver a causa:
        return jsonify({'error': str(e)}), 500
        #return jsonify({'error': 'Erro interno do servidor'}), 500

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

# ==================== ROTAS DE ADMIN ====================

@experience_bp.route('/admin/experiences/bulk-upload', methods=['POST'])
def admin_bulk_upload_experiences():
    """Upload em lote de experiências via planilha (Excel/CSV)"""
    try:
        current_app.logger.info("Iniciando bulk upload de experiências")
        
        # Verificar se há arquivo no request
        if 'file' not in request.files:
            current_app.logger.error("Nenhum arquivo enviado")
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        current_app.logger.info(f"Arquivo recebido: {file.filename}")
        
        if file.filename == '':
            current_app.logger.error("Nenhum arquivo selecionado")
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Verificar extensão do arquivo
        allowed_extensions = {'xlsx', 'xls', 'csv'}
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        
        if file_extension not in allowed_extensions:
            return jsonify({'error': 'Formato de arquivo não suportado. Use Excel (.xlsx, .xls) ou CSV (.csv)'}), 400
        
        # Ler o arquivo
        try:
            current_app.logger.info(f"Lendo arquivo {file_extension}")
            if file_extension == 'csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
            current_app.logger.info(f"Arquivo lido com {len(df)} linhas")
        except Exception as e:
            current_app.logger.error(f"Erro ao ler arquivo: {str(e)}")
            return jsonify({'error': f'Erro ao ler arquivo: {str(e)}'}), 400
        
        # Validar colunas obrigatórias
        required_columns = ['name', 'description', 'address', 'latitude', 'longitude']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            current_app.logger.error(f"Colunas ausentes: {missing_columns}")
            return jsonify({
                'error': f'Colunas obrigatórias ausentes: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'available_columns': list(df.columns)
            }), 400
        
        current_app.logger.info("Iniciando processamento das linhas")
        
        # Processar cada linha
        created_experiences = []
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Validar dados obrigatórios
                if pd.isna(row['name']) or pd.isna(row['description']) or pd.isna(row['address']):
                    errors.append(f'Linha {index + 2}: Campos obrigatórios não podem estar vazios')
                    continue
                
                # Validar coordenadas
                try:
                    latitude = float(row['latitude'])
                    longitude = float(row['longitude'])
                    
                    if not (-90 <= latitude <= 90):
                        errors.append(f'Linha {index + 2}: Latitude deve estar entre -90 e 90')
                        continue
                    
                    if not (-180 <= longitude <= 180):
                        errors.append(f'Linha {index + 2}: Longitude deve estar entre -180 e 180')
                        continue
                    
                    point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)
                except (ValueError, TypeError):
                    errors.append(f'Linha {index + 2}: Latitude e longitude devem ser números válidos')
                    continue
                
                # Validar categoria se fornecida
                category_id = None
                if 'category_id' in df.columns and not pd.isna(row['category_id']):
                    category = ExperienceCategory.query.get(row['category_id'])
                    if not category:
                        errors.append(f'Linha {index + 2}: Categoria não encontrada')
                        continue
                    category_id = row['category_id']
                
                # Criar experiência
                experience = Experience(
                    name=str(row['name']).strip(),
                    description=str(row['description']).strip(),
                    category_id=category_id,
                    address=str(row['address']).strip(),
                    location=point,
                    phone=str(row['phone']).strip() if 'phone' in df.columns and not pd.isna(row['phone']) else None,
                    website_url=str(row['website_url']).strip() if 'website_url' in df.columns and not pd.isna(row['website_url']) else None,
                    instagram_handle=str(row['instagram_handle']).strip() if 'instagram_handle' in df.columns and not pd.isna(row['instagram_handle']) else None,
                    opening_hours=row['opening_hours'] if 'opening_hours' in df.columns and not pd.isna(row['opening_hours']) else {},
                    price_range=int(row['price_range']) if 'price_range' in df.columns and not pd.isna(row['price_range']) else None,
                    is_hidden_gem=bool(row['is_hidden_gem']) if 'is_hidden_gem' in df.columns and not pd.isna(row['is_hidden_gem']) else False,
                    created_by=request.args.get('created_by')  # ID do admin que fez o upload
                )
                
                db.session.add(experience)
                created_experiences.append(experience)
                
            except Exception as e:
                errors.append(f'Linha {index + 2}: {str(e)}')
                continue
        
        # Commit das experiências válidas
        if created_experiences:
            current_app.logger.info(f"Fazendo commit de {len(created_experiences)} experiências")
            db.session.commit()
            current_app.logger.info("Commit realizado com sucesso")
        
        current_app.logger.info(f"Bulk upload concluído: {len(created_experiences)} criadas, {len(errors)} erros")
        
        return jsonify({
            'message': f'Upload concluído. {len(created_experiences)} experiências criadas.',
            'created_count': len(created_experiences),
            'errors': errors,
            'created_experiences': [exp.to_dict() for exp in created_experiences]
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Erro no bulk upload: {str(e)}")
        db.session.rollback()
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@experience_bp.route('/admin/experiences/template', methods=['GET'])
def admin_get_upload_template():
    """Retorna template para upload de experiências"""
    try:
        # Criar template de exemplo
        template_data = {
            'columns': [
                'name',
                'description', 
                'address',
                'latitude',
                'longitude',
                'category_id',
                'phone',
                'website_url',
                'instagram_handle',
                'price_range',
                'is_hidden_gem'
            ],
            'required_columns': ['name', 'description', 'address', 'latitude', 'longitude'],
            'example_data': [
                {
                    'name': 'Restaurante Exemplo',
                    'description': 'Melhor restaurante da cidade',
                    'address': 'Rua das Flores, 123',
                    'latitude': -23.5505,
                    'longitude': -46.6333,
                    'category_id': 1,
                    'phone': '(11) 99999-9999',
                    'website_url': 'https://exemplo.com',
                    'instagram_handle': '@exemplo',
                    'price_range': 2,
                    'is_hidden_gem': True
                }
            ],
            'price_range_options': {
                1: 'Barato (até R$ 30)',
                2: 'Moderado (R$ 30 - R$ 80)',
                3: 'Caro (R$ 80 - R$ 150)',
                4: 'Muito caro (acima de R$ 150)'
            },
            'instructions': [
                '1. Use Excel (.xlsx, .xls) ou CSV (.csv)',
                '2. Campos obrigatórios: name, description, address, latitude, longitude',
                '3. Latitude: -90 a 90, Longitude: -180 a 180',
                '4. category_id: ID da categoria (opcional)',
                '5. price_range: 1-4 (opcional)',
                '6. is_hidden_gem: true/false (opcional)'
            ]
        }
        
        return jsonify(template_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/admin/experiences/<experience_id>', methods=['PUT'])
def admin_update_experience(experience_id):
    """Atualiza uma experiência (rota de admin com mais permissões)"""
    try:
        experience = Experience.query.get(experience_id)
        
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados por admin (incluindo campos sensíveis)
        updatable_fields = [
            'name', 'description', 'category_id', 'address', 
            'latitude', 'longitude', 'phone', 'website_url', 
            'instagram_handle', 'opening_hours', 'price_range', 
            'is_hidden_gem', 'is_verified', 'is_active'
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

@experience_bp.route('/admin/experiences/<experience_id>', methods=['DELETE'])
def admin_delete_experience(experience_id):
    """Deleta uma experiência (rota de admin)"""
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

# Configurações para upload de imagens
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file, experience_id):
    """Salva uma imagem e retorna a URL"""
    try:
        # Criar diretório se não existir
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', str(experience_id))
        os.makedirs(upload_folder, exist_ok=True)
        
        # Gerar nome único para o arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(upload_folder, unique_filename)
        
        # Salvar arquivo
        file.save(filepath)
        
        # Retornar URL relativa
        return f"/static/uploads/{experience_id}/{unique_filename}"
        
    except Exception as e:
        current_app.logger.error(f"Erro ao salvar imagem: {str(e)}")
        return None

@experience_bp.route('/experiences/<experience_id>/photos', methods=['POST'])
def upload_photos(experience_id):
    """Upload de fotos para uma experiência"""
    try:
        experience = Experience.query.get(experience_id)
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        # Verificar se há arquivos
        if 'photos' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        files = request.files.getlist('photos')
        if not files or files[0].filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        uploaded_urls = []
        
        for file in files:
            if file and allowed_file(file.filename):
                # Verificar tamanho do arquivo
                file.seek(0, 2)  # Ir para o final do arquivo
                file_size = file.tell()
                file.seek(0)  # Voltar para o início
                
                if file_size > MAX_FILE_SIZE:
                    return jsonify({'error': f'Arquivo {file.filename} é muito grande. Máximo 5MB.'}), 400
                
                # Salvar imagem
                image_url = save_image(file, experience_id)
                if image_url:
                    uploaded_urls.append(image_url)
                else:
                    return jsonify({'error': f'Erro ao salvar {file.filename}'}), 500
        
        # Atualizar lista de fotos da experiência
        current_photos = experience.photos or []
        experience.photos = current_photos + uploaded_urls
        experience.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(uploaded_urls)} foto(s) enviada(s) com sucesso',
            'photos': uploaded_urls,
            'total_photos': len(experience.photos)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro no upload de fotos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/<experience_id>/photos', methods=['DELETE'])
def delete_photos(experience_id):
    """Remove fotos de uma experiência"""
    try:
        experience = Experience.query.get(experience_id)
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        data = request.get_json()
        photo_urls = data.get('photo_urls', [])
        
        if not photo_urls:
            return jsonify({'error': 'Nenhuma foto especificada para remoção'}), 400
        
        current_photos = experience.photos or []
        updated_photos = [photo for photo in current_photos if photo not in photo_urls]
        
        # Remover arquivos físicos
        for photo_url in photo_urls:
            try:
                if photo_url.startswith('/static/uploads/'):
                    file_path = os.path.join(current_app.root_path, photo_url.lstrip('/'))
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                current_app.logger.warning(f"Erro ao remover arquivo {photo_url}: {str(e)}")
        
        experience.photos = updated_photos
        experience.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'{len(photo_urls)} foto(s) removida(s) com sucesso',
            'total_photos': len(updated_photos)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao remover fotos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@experience_bp.route('/experiences/<experience_id>/photos/reorder', methods=['PUT'])
def reorder_photos(experience_id):
    """Reordena as fotos de uma experiência"""
    try:
        experience = Experience.query.get(experience_id)
        if not experience:
            return jsonify({'error': 'Experiência não encontrada'}), 404
        
        data = request.get_json()
        new_order = data.get('photo_order', [])
        
        if not new_order:
            return jsonify({'error': 'Nova ordem não especificada'}), 400
        
        current_photos = experience.photos or []
        
        # Verificar se todas as fotos na nova ordem existem
        if not all(photo in current_photos for photo in new_order):
            return jsonify({'error': 'Algumas fotos especificadas não existem'}), 400
        
        experience.photos = new_order
        experience.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Fotos reordenadas com sucesso',
            'photos': new_order
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Erro ao reordenar fotos: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

