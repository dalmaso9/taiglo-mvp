from flask import Blueprint, request, jsonify
from src.models.experience import ExperienceCategory, db

category_bp = Blueprint('category', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    """Lista todas as categorias de experiências"""
    try:
        categories = ExperienceCategory.query.order_by(ExperienceCategory.name.asc()).all()
        
        return jsonify({
            'categories': [category.to_dict() for category in categories],
            'total': len(categories)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@category_bp.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    """Busca uma categoria específica"""
    try:
        category = ExperienceCategory.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        return jsonify({
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Erro interno do servidor'}), 500

@category_bp.route('/categories', methods=['POST'])
def create_category():
    """Cria uma nova categoria"""
    try:
        data = request.get_json()
        
        # Validar campos obrigatórios
        if not data.get('name'):
            return jsonify({'error': 'Nome da categoria é obrigatório'}), 400
        
        # Verificar se categoria já existe
        existing_category = ExperienceCategory.query.filter_by(name=data['name']).first()
        if existing_category:
            return jsonify({'error': 'Categoria já existe'}), 409
        
        # Criar nova categoria
        category = ExperienceCategory(
            name=data['name'].strip(),
            description=data.get('description', '').strip() if data.get('description') else None,
            icon_url=data.get('icon_url', '').strip() if data.get('icon_url') else None,
            color_hex=data.get('color_hex', '#000000')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria criada com sucesso',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@category_bp.route('/categories/<category_id>', methods=['PUT'])
def update_category(category_id):
    """Atualiza uma categoria existente"""
    try:
        category = ExperienceCategory.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        data = request.get_json()
        
        # Campos que podem ser atualizados
        updatable_fields = ['name', 'description', 'icon_url', 'color_hex']
        
        for field in updatable_fields:
            if field in data:
                if field == 'name':
                    # Verificar se o novo nome já existe (exceto para a categoria atual)
                    existing = ExperienceCategory.query.filter(
                        ExperienceCategory.name == data[field],
                        ExperienceCategory.id != category_id
                    ).first()
                    if existing:
                        return jsonify({'error': 'Nome da categoria já existe'}), 409
                
                setattr(category, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria atualizada com sucesso',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@category_bp.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    """Deleta uma categoria"""
    try:
        category = ExperienceCategory.query.get(category_id)
        
        if not category:
            return jsonify({'error': 'Categoria não encontrada'}), 404
        
        # Verificar se há experiências usando esta categoria
        if category.experiences:
            return jsonify({
                'error': 'Não é possível deletar categoria que possui experiências associadas'
            }), 409
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'message': 'Categoria deletada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

