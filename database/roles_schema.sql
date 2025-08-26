-- Schema para sistema de roles e permissões
-- Baseado nas tabelas existentes: roles, permissions, role_permissions, user_roles

-- Tabela de roles
CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de permissões
CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    resource VARCHAR(50) NOT NULL, -- 'experiences', 'reviews', 'users', etc.
    action VARCHAR(50) NOT NULL,   -- 'create', 'read', 'update', 'delete', 'admin'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relacionamento entre roles e permissões
CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- Tabela de relacionamento entre usuários e roles
CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON permissions(resource, action);

-- Trigger para atualizar updated_at em roles (remover se existir e recriar)
DROP TRIGGER IF EXISTS update_roles_updated_at ON roles;
CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON roles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir roles padrão
INSERT INTO roles (name, description) VALUES
('user', 'Usuário padrão do sistema'),
('moderator', 'Moderador com permissões limitadas de administração'),
('admin', 'Administrador com acesso total ao sistema')
ON CONFLICT (name) DO NOTHING;

-- Inserir permissões do sistema
INSERT INTO permissions (name, description, resource, action) VALUES
-- Permissões de experiências
('experiences.read', 'Visualizar experiências', 'experiences', 'read'),
('experiences.create', 'Criar experiências', 'experiences', 'create'),
('experiences.update', 'Atualizar experiências', 'experiences', 'update'),
('experiences.delete', 'Deletar experiências', 'experiences', 'delete'),
('experiences.admin', 'Acesso administrativo a experiências', 'experiences', 'admin'),

-- Permissões de reviews
('reviews.read', 'Visualizar reviews', 'reviews', 'read'),
('reviews.create', 'Criar reviews', 'reviews', 'create'),
('reviews.update', 'Atualizar reviews', 'reviews', 'update'),
('reviews.delete', 'Deletar reviews', 'reviews', 'delete'),
('reviews.moderate', 'Moderar reviews', 'reviews', 'moderate'),

-- Permissões de usuários
('users.read', 'Visualizar usuários', 'users', 'read'),
('users.create', 'Criar usuários', 'users', 'create'),
('users.update', 'Atualizar usuários', 'users', 'update'),
('users.delete', 'Deletar usuários', 'users', 'delete'),
('users.admin', 'Acesso administrativo a usuários', 'users', 'admin'),

-- Permissões de categorias
('categories.read', 'Visualizar categorias', 'categories', 'read'),
('categories.create', 'Criar categorias', 'categories', 'create'),
('categories.update', 'Atualizar categorias', 'categories', 'update'),
('categories.delete', 'Deletar categorias', 'categories', 'delete'),

-- Permissões de sistema
('system.admin', 'Acesso administrativo total ao sistema', 'system', 'admin'),
('system.reports', 'Acesso a relatórios do sistema', 'system', 'reports'),
('system.backup', 'Acesso a backup e restauração', 'system', 'backup')
ON CONFLICT (name) DO NOTHING;

-- Atribuir permissões aos roles
-- Role: user
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'user' AND p.name IN (
    'experiences.read',
    'reviews.read',
    'reviews.create',
    'categories.read'
)
ON CONFLICT DO NOTHING;

-- Role: moderator
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'moderator' AND p.name IN (
    'experiences.read',
    'experiences.create',
    'experiences.update',
    'reviews.read',
    'reviews.create',
    'reviews.update',
    'reviews.moderate',
    'categories.read',
    'users.read'
)
ON CONFLICT DO NOTHING;

-- Role: admin
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p
WHERE r.name = 'admin' AND p.name IN (
    'experiences.read',
    'experiences.create',
    'experiences.update',
    'experiences.delete',
    'experiences.admin',
    'reviews.read',
    'reviews.create',
    'reviews.update',
    'reviews.delete',
    'reviews.moderate',
    'users.read',
    'users.create',
    'users.update',
    'users.delete',
    'users.admin',
    'categories.read',
    'categories.create',
    'categories.update',
    'categories.delete',
    'system.admin',
    'system.reports',
    'system.backup'
)
ON CONFLICT DO NOTHING;

-- Função para verificar se usuário tem permissão
CREATE OR REPLACE FUNCTION user_has_permission(user_uuid UUID, permission_name VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_roles ur
        JOIN role_permissions rp ON ur.role_id = rp.role_id
        JOIN permissions p ON rp.permission_id = p.id
        JOIN roles r ON ur.role_id = r.id
        WHERE ur.user_id = user_uuid
        AND p.name = permission_name
        AND r.is_active = TRUE
    );
END;
$$ LANGUAGE plpgsql;

-- Função para obter todas as permissões de um usuário
CREATE OR REPLACE FUNCTION get_user_permissions(user_uuid UUID)
RETURNS TABLE(permission_name VARCHAR, resource VARCHAR, action VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT p.name, p.resource, p.action
    FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    JOIN roles r ON ur.role_id = r.id
    WHERE ur.user_id = user_uuid
    AND r.is_active = TRUE
    ORDER BY p.resource, p.action;
END;
$$ LANGUAGE plpgsql;

-- Função para obter todos os roles de um usuário
CREATE OR REPLACE FUNCTION get_user_roles(user_uuid UUID)
RETURNS TABLE(role_name VARCHAR, role_description TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT r.name, r.description
    FROM user_roles ur
    JOIN roles r ON ur.role_id = r.id
    WHERE ur.user_id = user_uuid
    AND r.is_active = TRUE
    ORDER BY r.name;
END;
$$ LANGUAGE plpgsql;
