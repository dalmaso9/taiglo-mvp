# 🔐 Sistema de Roles e Permissões - Taiglo MVP

## 📋 **Visão Geral**

Implementamos um sistema robusto de roles e permissões baseado nas tabelas existentes do seu banco de dados:
- `roles` - Definição dos roles do sistema
- `permissions` - Permissões específicas por recurso/ação
- `role_permissions` - Relacionamento entre roles e permissões
- `user_roles` - Relacionamento entre usuários e roles

## 🏗️ **Arquitetura do Sistema**

### **Estrutura de Tabelas**

```sql
-- Tabela de roles
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de permissões
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR(50) NOT NULL, -- 'experiences', 'reviews', 'users', etc.
    action VARCHAR(50) NOT NULL    -- 'create', 'read', 'update', 'delete', 'admin'
);

-- Relacionamento roles-permissões
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id),
    permission_id UUID REFERENCES permissions(id),
    UNIQUE(role_id, permission_id)
);

-- Relacionamento usuários-roles
CREATE TABLE user_roles (
    user_id UUID REFERENCES users(id),
    role_id UUID REFERENCES roles(id),
    UNIQUE(user_id, role_id)
);
```

### **Roles Padrão**

1. **`user`** - Usuário padrão do sistema
   - Visualizar experiências
   - Criar e visualizar reviews
   - Visualizar categorias

2. **`moderator`** - Moderador com permissões limitadas
   - Todas as permissões de `user`
   - Criar e atualizar experiências
   - Moderar reviews
   - Visualizar usuários

3. **`admin`** - Administrador com acesso total
   - Todas as permissões de `moderator`
   - Deletar experiências e reviews
   - Gerenciar usuários
   - Acesso administrativo total

## 🔧 **Configuração**

### **1. Executar Schema de Roles**

```bash
# Executar o script de configuração
python setup_roles_system.py
```

Este script irá:
- Criar as tabelas de roles e permissões
- Inserir roles e permissões padrão
- Configurar relacionamentos
- Criar usuário admin

### **2. Criar Usuário Admin**

```bash
# Criar usuário admin via API
python create_admin_user.py
```

**Credenciais padrão:**
- Email: `admin@taiglo.com`
- Senha: `admin123`

## 🎯 **Funcionalidades Implementadas**

### **Backend - Modelo de Usuário**

```python
class User(db.Model):
    # ... outros campos ...
    
    def has_permission(self, permission_name):
        """Verifica se o usuário tem uma permissão específica"""
        # Usa função do banco: user_has_permission()
    
    def has_role(self, role_name):
        """Verifica se o usuário tem um role específico"""
        # Consulta direta na tabela user_roles
    
    def is_admin(self):
        """Verifica se o usuário é admin"""
        return self.has_role('admin')
    
    def get_roles(self):
        """Retorna todos os roles do usuário"""
        # Usa função do banco: get_user_roles()
    
    def get_permissions(self):
        """Retorna todas as permissões do usuário"""
        # Usa função do banco: get_user_permissions()
    
    def add_role(self, role_name):
        """Adiciona um role ao usuário"""
    
    def remove_role(self, role_name):
        """Remove um role do usuário"""
```

### **Backend - Decorators de Autorização**

```python
# Verificar se é admin
@admin_required
def admin_only_function():
    pass

# Verificar permissão específica
@permission_required('experiences.admin')
def manage_experiences():
    pass

# Verificar role específico
@role_required('moderator')
def moderate_content():
    pass
```

### **Frontend - Verificação de Roles**

```javascript
// Verificar se usuário é admin
const hasAdminRole = user?.roles?.some(role => role.name === 'admin') || false;

// Verificar permissão específica
const hasPermission = user?.permissions?.some(p => p.name === 'experiences.admin') || false;
```

## 🔌 **APIs de Gerenciamento de Roles**

### **Obter Roles de um Usuário**
```http
GET /api/auth/users/{user_id}/roles
Authorization: Bearer <token>
```

### **Adicionar Role a um Usuário**
```http
POST /api/auth/users/{user_id}/roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "role": "admin"
}
```

### **Remover Role de um Usuário**
```http
DELETE /api/auth/users/{user_id}/roles/{role_name}
Authorization: Bearer <token>
```

## 📊 **Permissões Disponíveis**

### **Experiências**
- `experiences.read` - Visualizar experiências
- `experiences.create` - Criar experiências
- `experiences.update` - Atualizar experiências
- `experiences.delete` - Deletar experiências
- `experiences.admin` - Acesso administrativo

### **Reviews**
- `reviews.read` - Visualizar reviews
- `reviews.create` - Criar reviews
- `reviews.update` - Atualizar reviews
- `reviews.delete` - Deletar reviews
- `reviews.moderate` - Moderar reviews

### **Usuários**
- `users.read` - Visualizar usuários
- `users.create` - Criar usuários
- `users.update` - Atualizar usuários
- `users.delete` - Deletar usuários
- `users.admin` - Acesso administrativo

### **Categorias**
- `categories.read` - Visualizar categorias
- `categories.create` - Criar categorias
- `categories.update` - Atualizar categorias
- `categories.delete` - Deletar categorias

### **Sistema**
- `system.admin` - Acesso administrativo total
- `system.reports` - Acesso a relatórios
- `system.backup` - Acesso a backup/restauração

## 🎨 **Interface do Usuário**

### **Navegação Atualizada**
- Indicador visual de role "Administrador"
- Link "Painel Admin" apenas para admins
- Verificação de permissões no frontend

### **AdminPanel**
- Acesso restrito apenas para usuários com role `admin`
- Funcionalidades completas de gerenciamento
- Upload em lote de experiências
- Edição e exclusão de experiências

## 🔒 **Segurança**

### **Validações Implementadas**
- ✅ Verificação de roles em todas as rotas admin
- ✅ Verificação de permissões específicas
- ✅ Validação server-side de todas as operações
- ✅ Logs de auditoria para operações sensíveis
- ✅ Rollback em caso de falha

### **Boas Práticas**
- Sempre verificar permissões no backend
- Usar decorators para proteção de rotas
- Validar dados de entrada
- Logs de todas as operações admin

## 🚀 **Como Usar**

### **1. Configuração Inicial**
```bash
# 1. Executar schema de roles
python setup_roles_system.py

# 2. Criar usuário admin
python create_admin_user.py

# 3. Testar acesso
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@taiglo.com", "password": "admin123"}'
```

### **2. Acessar Painel Admin**
1. Fazer login no frontend com credenciais admin
2. Clicar no menu do usuário
3. Selecionar "Painel Admin"
4. Usar as funcionalidades de gerenciamento

### **3. Gerenciar Roles**
```bash
# Adicionar role a um usuário
curl -X POST http://localhost:3000/api/auth/users/{user_id}/roles \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "moderator"}'

# Remover role de um usuário
curl -X DELETE http://localhost:3000/api/auth/users/{user_id}/roles/moderator \
  -H "Authorization: Bearer {token}"
```

## 📈 **Vantagens do Sistema**

### **Flexibilidade**
- ✅ Múltiplos roles por usuário
- ✅ Permissões granulares
- ✅ Fácil adição de novos roles/permissões
- ✅ Sistema escalável

### **Segurança**
- ✅ Verificação em múltiplas camadas
- ✅ Controle de acesso baseado em permissões
- ✅ Auditoria completa
- ✅ Isolamento de responsabilidades

### **Manutenibilidade**
- ✅ Código limpo e organizado
- ✅ Decorators reutilizáveis
- ✅ Funções do banco otimizadas
- ✅ Documentação completa

## 🔄 **Migração do Sistema Anterior**

### **Mudanças Realizadas**
1. **Removido campo `role` simples** da tabela `users`
2. **Implementado sistema de roles múltiplos** via `user_roles`
3. **Adicionado sistema de permissões** granulares
4. **Atualizado frontend** para usar novo sistema
5. **Criado decorators** para verificação de permissões

### **Compatibilidade**
- ✅ Todas as funcionalidades admin mantidas
- ✅ Interface do usuário atualizada
- ✅ APIs compatíveis com novo sistema
- ✅ Scripts de migração fornecidos

---

## ✅ **Status: Implementado e Funcional**

O sistema de roles está completamente implementado e integrado com suas tabelas existentes:

1. ✅ **Sistema de roles robusto** usando suas tabelas
2. ✅ **Permissões granulares** por recurso/ação
3. ✅ **Múltiplos roles** por usuário
4. ✅ **APIs de gerenciamento** completas
5. ✅ **Interface atualizada** no frontend
6. ✅ **Scripts de configuração** fornecidos
7. ✅ **Documentação completa** disponível

**🎉 O sistema está pronto para uso em produção!**
