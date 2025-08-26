-- Schema para o banco de dados do Taiglo MVP
-- PostgreSQL com extensão PostGIS para dados geoespaciais

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabela de usuários
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    date_of_birth DATE,
    profile_picture_url TEXT,
    bio TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_local_guide BOOLEAN DEFAULT FALSE,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de categorias de experiências
CREATE TABLE experience_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon_url TEXT,
    color_hex VARCHAR(7) DEFAULT '#000000',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de experiências locais
CREATE TABLE experiences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category_id UUID REFERENCES experience_categories(id),
    address TEXT NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL, -- PostGIS para coordenadas lat/lng
    phone VARCHAR(20),
    website_url TEXT,
    instagram_handle VARCHAR(100),
    opening_hours JSONB DEFAULT '{}',
    price_range INTEGER CHECK (price_range >= 1 AND price_range <= 4), -- 1-4 ($-$$$$)
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INTEGER DEFAULT 0,
    is_hidden_gem BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    authenticity_score DECIMAL(3,2) DEFAULT 0.00,
    photos JSONB DEFAULT '[]', -- Array de URLs das fotos da experiência
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de avaliações
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    experience_id UUID REFERENCES experiences(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(255),
    content TEXT NOT NULL,
    photos JSONB DEFAULT '[]', -- Array de URLs das fotos
    visit_date DATE,
    is_verified BOOLEAN DEFAULT FALSE,
    authenticity_score DECIMAL(3,2) DEFAULT 0.00,
    helpful_votes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(experience_id, user_id) -- Um usuário só pode avaliar uma experiência uma vez
);

-- Tabela de badges/conquistas
CREATE TABLE badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    icon_url TEXT,
    criteria JSONB NOT NULL, -- Critérios para ganhar o badge
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de badges dos usuários
CREATE TABLE user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, badge_id)
);

-- Tabela de favoritos
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    experience_id UUID REFERENCES experiences(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, experience_id)
);

-- Índices para performance
CREATE INDEX idx_experiences_location ON experiences USING GIST (location);
CREATE INDEX idx_experiences_category ON experiences(category_id);
CREATE INDEX idx_experiences_rating ON experiences(average_rating DESC);
CREATE INDEX idx_reviews_experience ON reviews(experience_id);
CREATE INDEX idx_reviews_user ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_users_email ON users(email);

-- Função para atualizar o timestamp de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_experiences_updated_at BEFORE UPDATE ON experiences FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para atualizar a média de avaliações de uma experiência
CREATE OR REPLACE FUNCTION update_experience_rating()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE experiences 
    SET 
        average_rating = (
            SELECT COALESCE(AVG(rating), 0) 
            FROM reviews 
            WHERE experience_id = COALESCE(NEW.experience_id, OLD.experience_id)
        ),
        total_reviews = (
            SELECT COUNT(*) 
            FROM reviews 
            WHERE experience_id = COALESCE(NEW.experience_id, OLD.experience_id)
        )
    WHERE id = COALESCE(NEW.experience_id, OLD.experience_id);
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Triggers para atualizar rating automaticamente
CREATE TRIGGER update_experience_rating_on_insert AFTER INSERT ON reviews FOR EACH ROW EXECUTE FUNCTION update_experience_rating();
CREATE TRIGGER update_experience_rating_on_update AFTER UPDATE ON reviews FOR EACH ROW EXECUTE FUNCTION update_experience_rating();
CREATE TRIGGER update_experience_rating_on_delete AFTER DELETE ON reviews FOR EACH ROW EXECUTE FUNCTION update_experience_rating();

