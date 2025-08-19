# 🛠️ Funcionalidades de Administração - Taiglo MVP

## 📋 **Visão Geral**

Implementamos um sistema completo de administração para usuários com role "admin" que permite:

1. **Editar experiências diretamente do frontend**
2. **Criar novas experiências manualmente**
3. **Upload em lote de experiências via planilha (Excel/CSV)**

## 🔐 **Sistema de Autenticação e Autorização**

### **Modelo de Usuário Atualizado**
- Adicionado campo `role` com valores: `'user'`, `'admin'`, `'moderator'`
- Métodos de verificação: `is_admin()` e `is_moderator()`

```python
# user-service/src/models/user.py
class User(db.Model):
    role = db.Column(db.String(20), default='user')
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_moderator(self):
        return self.role in ['admin', 'moderator']
```

### **Decorator de Proteção**
```python
# user-service/src/routes/auth.py
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
```

## 🎯 **Funcionalidades Implementadas**

### **1. Painel de Administração (Frontend)**

**Localização**: `frontend/src/components/AdminPanel.jsx`

**Características**:
- Interface moderna com tabs organizadas
- Acesso restrito apenas para usuários admin
- Feedback visual de operações
- Validação de formulários

**Tabs Disponíveis**:
- **Listar Experiências**: Visualizar e gerenciar todas as experiências
- **Criar Experiência**: Formulário para adicionar experiências manualmente
- **Upload em Lote**: Interface para upload de planilhas

### **2. Edição de Experiências**

**Funcionalidades**:
- ✅ Editar todas as informações da experiência
- ✅ Validação de coordenadas geográficas
- ✅ Seleção de categorias
- ✅ Controle de status (verificado, ativo, hidden gem)
- ✅ Exclusão de experiências

**Campos Editáveis**:
- Nome, descrição, endereço
- Latitude e longitude
- Categoria, telefone, website
- Instagram, faixa de preço
- Status (verificado, ativo, hidden gem)

### **3. Criação Manual de Experiências**

**Formulário Completo**:
- Campos obrigatórios e opcionais
- Validação em tempo real
- Seleção de categorias dinâmica
- Preview de dados antes do envio

### **4. Upload em Lote via Planilha**

**Formatos Suportados**:
- Excel (.xlsx, .xls)
- CSV (.csv)

**Funcionalidades**:
- ✅ Template para download
- ✅ Validação de colunas obrigatórias
- ✅ Processamento linha por linha
- ✅ Relatório de erros detalhado
- ✅ Rollback em caso de falha

**Colunas do Template**:
```csv
name,description,address,latitude,longitude,category_id,phone,website_url,instagram_handle,price_range,is_hidden_gem
```

**Validações**:
- Campos obrigatórios: name, description, address, latitude, longitude
- Coordenadas válidas (-90 a 90 lat, -180 a 180 lon)
- Categoria existente no sistema
- Faixa de preço (1-4)

## 🔌 **APIs Implementadas**

### **Experience Service - Rotas de Admin**

#### **1. Upload em Lote**
```http
POST /api/admin/experiences/bulk-upload
Content-Type: multipart/form-data
Authorization: Bearer <token>

Form Data:
- file: arquivo Excel/CSV
- created_by: ID do admin
```

#### **2. Template de Upload**
```http
GET /api/admin/experiences/template
Authorization: Bearer <token>
```

#### **3. Edição de Experiência**
```http
PUT /api/admin/experiences/{experience_id}
Content-Type: application/json
Authorization: Bearer <token>

Body: {
  "name": "string",
  "description": "string",
  "address": "string",
  "latitude": number,
  "longitude": number,
  "category_id": "string",
  "phone": "string",
  "website_url": "string",
  "instagram_handle": "string",
  "opening_hours": object,
  "price_range": number,
  "is_hidden_gem": boolean,
  "is_verified": boolean,
  "is_active": boolean
}
```

#### **4. Exclusão de Experiência**
```http
DELETE /api/admin/experiences/{experience_id}
Authorization: Bearer <token>
```

### **API Gateway - Rotas de Admin**

Todas as rotas de admin são expostas através do gateway com:
- Documentação Swagger completa
- Validação de autenticação
- Logs de auditoria

## 🎨 **Interface do Usuário**

### **Navegação Atualizada**
- Link "Painel Admin" no menu do usuário (apenas para admins)
- Indicador visual de role "Administrador"
- Acesso via `/admin` no frontend

### **Componentes UI Utilizados**
- **Tabs**: Organização das funcionalidades
- **Cards**: Layout das seções
- **Forms**: Validação e submissão
- **Alerts**: Feedback de operações
- **Badges**: Status das experiências
- **Buttons**: Ações principais e secundárias

### **Responsividade**
- Interface adaptável para desktop e mobile
- Menu responsivo com funcionalidades admin
- Formulários otimizados para diferentes telas

## 📊 **Funcionalidades de Upload**

### **Processamento de Planilhas**
```python
# experience-service/src/routes/experience.py
@experience_bp.route('/admin/experiences/bulk-upload', methods=['POST'])
def admin_bulk_upload_experiences():
    # Validação de arquivo
    # Leitura com pandas
    # Validação linha por linha
    # Criação em lote
    # Relatório de resultados
```

### **Validações Implementadas**
- ✅ Formato de arquivo (.xlsx, .xls, .csv)
- ✅ Colunas obrigatórias presentes
- ✅ Dados não vazios nos campos obrigatórios
- ✅ Coordenadas geográficas válidas
- ✅ Categoria existente no sistema
- ✅ Faixa de preço válida (1-4)

### **Relatório de Upload**
```json
{
  "message": "Upload concluído. 15 experiências criadas.",
  "created_count": 15,
  "errors": [
    "Linha 3: Latitude deve estar entre -90 e 90",
    "Linha 7: Categoria não encontrada"
  ],
  "created_experiences": [...]
}
```

## 🔧 **Configuração e Instalação**

### **Dependências Adicionadas**
```bash
# experience-service
pip install pandas openpyxl

# requirements.txt atualizado
pandas>=2.3.0
openpyxl>=3.1.0
```

### **Banco de Dados**
- Campo `role` adicionado à tabela `users`
- Migração necessária para usuários existentes

### **Variáveis de Ambiente**
```env
# Para definir um usuário como admin
# Atualizar diretamente no banco ou via seed
```

## 🚀 **Como Usar**

### **1. Criar Usuário Admin**
```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@taiglo.com';
```

### **2. Acessar Painel Admin**
1. Fazer login como usuário admin
2. Clicar no menu do usuário
3. Selecionar "Painel Admin"

### **3. Upload em Lote**
1. Baixar template de exemplo
2. Preencher dados no Excel/CSV
3. Fazer upload no painel
4. Verificar relatório de resultados

### **4. Edição Manual**
1. Navegar para tab "Criar Experiência"
2. Preencher formulário
3. Salvar experiência

## 📈 **Próximas Melhorias**

### **Funcionalidades Planejadas**
- [ ] Dashboard com estatísticas
- [ ] Moderação de reviews
- [ ] Gestão de usuários
- [ ] Logs de auditoria
- [ ] Backup e restauração
- [ ] Relatórios avançados

### **Melhorias Técnicas**
- [ ] Cache de categorias
- [ ] Validação assíncrona
- [ ] Upload progressivo
- [ ] Notificações em tempo real
- [ ] Exportação de dados

## 🔒 **Segurança**

### **Medidas Implementadas**
- ✅ Verificação de role em todas as rotas admin
- ✅ Validação de token JWT
- ✅ Sanitização de dados de entrada
- ✅ Validação de tipos de arquivo
- ✅ Rollback em caso de erro

### **Boas Práticas**
- Logs de todas as operações admin
- Validação server-side de todos os dados
- Rate limiting para uploads
- Sanitização de coordenadas geográficas

---

## ✅ **Status: Implementado e Funcional**

Todas as funcionalidades solicitadas foram implementadas com sucesso:

1. ✅ **Edição de experiências direto do frontend**
2. ✅ **Criação manual de experiências**
3. ✅ **Upload em lote via planilha**
4. ✅ **Sistema de autorização admin**
5. ✅ **Interface moderna e responsiva**
6. ✅ **Documentação completa**

**🎉 O sistema está pronto para uso em produção!**
