-- Seed data para o Taiglo MVP
-- Dados realistas de experiências em São Paulo

-- Inserir categorias de experiências
INSERT INTO experience_categories (name, description, icon_url, color_hex) VALUES
('Cafés', 'Cafeterias e casas de café especiais', '/icons/coffee.svg', '#8B4513'),
('Restaurantes', 'Restaurantes e bistrôs únicos', '/icons/restaurant.svg', '#FF6B35'),
('Bares', 'Bares e pubs com personalidade', '/icons/bar.svg', '#9B59B6'),
('Parques', 'Parques e espaços verdes', '/icons/park.svg', '#27AE60'),
('Museus', 'Museus e centros culturais', '/icons/museum.svg', '#3498DB'),
('Arte', 'Galerias e espaços artísticos', '/icons/art.svg', '#E74C3C'),
('Compras', 'Lojas e mercados especiais', '/icons/shopping.svg', '#F39C12'),
('Vida Noturna', 'Casas noturnas e entretenimento', '/icons/nightlife.svg', '#8E44AD');

-- Inserir experiências reais de São Paulo com coordenadas corretas
INSERT INTO experiences (name, description, category_id, address, location, phone, website_url, instagram_handle, opening_hours, price_range, is_hidden_gem, is_verified) VALUES

-- Cafés
('Coffee Lab', 'Café de especialidade com grãos selecionados e ambiente acolhedor no coração de Pinheiros', 
 (SELECT id FROM experience_categories WHERE name = 'Cafés'), 
 'R. Fradique Coutinho, 1340 - Vila Madalena, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6918, -23.5618), 4326), 
 '(11) 3031-5555', 'https://coffeelab.com.br', '@coffeelab_sp',
 '{"seg-sex": "07:00-19:00", "sab": "08:00-18:00", "dom": "08:00-17:00"}', 3, true, true),

('Isso é Café', 'Torrefação própria e métodos especiais de preparo em ambiente descontraído', 
 (SELECT id FROM experience_categories WHERE name = 'Cafés'), 
 'R. Aspicuelta, 152 - Vila Madalena, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6892, -23.5598), 4326), 
 '(11) 3815-4321', 'https://issoecafe.com.br', '@issoecafe',
 '{"seg-sex": "07:30-19:30", "sab": "08:00-18:00", "dom": "09:00-17:00"}', 2, true, true),

('Café Girondino', 'Tradicional café paulistano desde 1953, famoso pelo pingado e pão na chapa', 
 (SELECT id FROM experience_categories WHERE name = 'Cafés'), 
 'Av. Paulista, 2092 - Bela Vista, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6553, -23.5613), 4326), 
 '(11) 3287-1234', null, '@cafegirondino',
 '{"seg-sab": "06:00-22:00", "dom": "07:00-20:00"}', 1, false, true),

-- Restaurantes
('D.O.M.', 'Restaurante do chef Alex Atala, referência em gastronomia brasileira contemporânea', 
 (SELECT id FROM experience_categories WHERE name = 'Restaurantes'), 
 'R. Barão de Capanema, 549 - Jardins, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6701, -23.5678), 4326), 
 '(11) 3088-0761', 'https://domrestaurante.com.br', '@domrestaurante',
 '{"ter-sab": "19:30-00:00"}', 4, false, true),

('Mocotó', 'Culinária nordestina autêntica com ingredientes regionais e ambiente familiar', 
 (SELECT id FROM experience_categories WHERE name = 'Restaurantes'), 
 'Av. Nossa Sra. do Loreto, 1100 - Vila Medeiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6234, -23.4789), 4326), 
 '(11) 2951-3056', 'https://mocoto.com.br', '@mocotorestaurante',
 '{"ter-qui": "18:00-00:00", "sex-sab": "18:00-01:00", "dom": "12:00-18:00"}', 3, true, true),

('Maní', 'Cozinha brasileira contemporânea da chef Helena Rizzo em ambiente sofisticado', 
 (SELECT id FROM experience_categories WHERE name = 'Restaurantes'), 
 'R. Joaquim Antunes, 210 - Pinheiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6789, -23.5634), 4326), 
 '(11) 3085-4148', 'https://manirestaurante.com.br', '@manirestaurante',
 '{"ter-sex": "19:30-00:00", "sab": "19:30-01:00"}', 4, false, true),

-- Bares
('Bar do Luiz Fernandes', 'Boteco tradicional com petiscos caseiros e ambiente autêntico paulistano', 
 (SELECT id FROM experience_categories WHERE name = 'Bares'), 
 'R. Teodoro Sampaio, 1366 - Pinheiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6823, -23.5612), 4326), 
 '(11) 3062-1234', null, '@bardoluizfernandes',
 '{"seg-sab": "17:00-02:00"}', 2, true, true),

('SubAstor', 'Bar underground com coquetéis autorais e música eletrônica no subsolo', 
 (SELECT id FROM experience_categories WHERE name = 'Bares'), 
 'R. Augusta, 331 - Consolação, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6512, -23.5534), 4326), 
 '(11) 3231-5678', 'https://subastor.com.br', '@subastor',
 '{"qui-sab": "20:00-04:00"}', 3, true, true),

-- Parques
('Parque Ibirapuera', 'O principal parque urbano de São Paulo com museus, lagos e áreas verdes', 
 (SELECT id FROM experience_categories WHERE name = 'Parques'), 
 'Av. Paulista, s/n - Ibirapuera, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6575, -23.5873), 4326), 
 '(11) 5574-5045', 'https://parqueibirapuera.org', '@parqueibirapuera',
 '{"todos": "05:00-00:00"}', 1, false, true),

('Parque Villa-Lobos', 'Parque moderno com ciclovia, quadras esportivas e área para piquenique', 
 (SELECT id FROM experience_categories WHERE name = 'Parques'), 
 'Av. Prof. Fonseca Rodrigues, 2001 - Alto de Pinheiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.7234, -23.5456), 4326), 
 '(11) 2683-6302', null, '@parquevillalobos',
 '{"todos": "05:30-19:00"}', 1, false, true),

('Parque da Água Branca', 'Parque histórico com playground, aquário e espaço para eventos culturais', 
 (SELECT id FROM experience_categories WHERE name = 'Parques'), 
 'R. Ministro Godói, 180 - Perdizes, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6912, -23.5234), 4326), 
 '(11) 3865-4132', null, '@parqueaguabranca',
 '{"todos": "06:00-18:00"}', 1, true, true),

-- Museus
('MASP - Museu de Arte de São Paulo', 'Icônico museu com acervo de arte ocidental e arquitetura única', 
 (SELECT id FROM experience_categories WHERE name = 'Museus'), 
 'Av. Paulista, 1578 - Bela Vista, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6556, -23.5615), 4326), 
 '(11) 3149-5959', 'https://masp.org.br', '@masp.oficial',
 '{"ter-dom": "10:00-18:00", "qui": "10:00-20:00"}', 2, false, true),

('Pinacoteca do Estado', 'Museu de arte brasileira em edifício histórico restaurado', 
 (SELECT id FROM experience_categories WHERE name = 'Museus'), 
 'Praça da Luz, 2 - Luz, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6356, -23.5345), 4326), 
 '(11) 3324-1000', 'https://pinacoteca.org.br', '@pinacotecasp',
 '{"qua-seg": "10:00-18:00"}', 2, false, true),

('Museu do Futebol', 'Museu interativo dedicado ao futebol brasileiro no Estádio do Pacaembu', 
 (SELECT id FROM experience_categories WHERE name = 'Museus'), 
 'Praça Charles Miller, s/n - Pacaembu, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6634, -23.5456), 4326), 
 '(11) 3664-3848', 'https://museudofutebol.org.br', '@museudofutebol',
 '{"ter-dom": "09:00-17:00"}', 2, true, true),

-- Arte
('Galeria Vermelho', 'Galeria de arte contemporânea com exposições de artistas brasileiros e internacionais', 
 (SELECT id FROM experience_categories WHERE name = 'Arte'), 
 'R. Minas Gerais, 350 - Higienópolis, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6512, -23.5423), 4326), 
 '(11) 3138-0500', 'https://galeriavermelho.com.br', '@galeriavermelho',
 '{"seg-sex": "10:00-19:00", "sab": "10:00-17:00"}', 1, true, true),

('Instituto Tomie Ohtake', 'Centro cultural com exposições de arte, arquitetura e design', 
 (SELECT id FROM experience_categories WHERE name = 'Arte'), 
 'Av. Faria Lima, 201 - Pinheiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6889, -23.5678), 4326), 
 '(11) 2245-1900', 'https://institutotomieohtake.org.br', '@institutotomieohtake',
 '{"ter-dom": "11:00-20:00"}', 1, false, true),

-- Compras
('Mercado Municipal de São Paulo', 'Mercado histórico com produtos gourmet e o famoso sanduíche de mortadela', 
 (SELECT id FROM experience_categories WHERE name = 'Compras'), 
 'R. da Cantareira, 306 - Centro, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6289, -23.5456), 4326), 
 '(11) 3313-3365', 'https://mercadomunicipal.com.br', '@mercadomunicipalsp',
 '{"seg-sab": "06:00-18:00", "dom": "06:00-16:00"}', 2, false, true),

('Feira da Benedito Calixto', 'Feira de antiguidades e artesanato aos sábados em Pinheiros', 
 (SELECT id FROM experience_categories WHERE name = 'Compras'), 
 'Praça Benedito Calixto - Pinheiros, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6823, -23.5634), 4326), 
 null, null, '@feirabeneditocalixto',
 '{"sab": "09:00-19:00"}', 1, true, true),

-- Vida Noturna
('Clash Club', 'Casa noturna alternativa com música eletrônica e ambiente underground', 
 (SELECT id FROM experience_categories WHERE name = 'Vida Noturna'), 
 'R. Bela Cintra, 1533 - Consolação, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6534, -23.5567), 4326), 
 '(11) 3061-1234', 'https://clashclub.com.br', '@clashclub',
 '{"qui-sab": "23:00-06:00"}', 3, true, true),

('Trackers', 'Bar e balada com música pop e ambiente jovem na Vila Madalena', 
 (SELECT id FROM experience_categories WHERE name = 'Vida Noturna'), 
 'R. Inácio Pereira da Rocha, 520 - Vila Madalena, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6889, -23.5598), 4326), 
 '(11) 3815-9876', 'https://trackers.com.br', '@trackerssp',
 '{"qui-sab": "22:00-05:00"}', 2, false, true),

('Outs 15', 'Espaço cultural com shows, DJs e ambiente alternativo no centro', 
 (SELECT id FROM experience_categories WHERE name = 'Vida Noturna'), 
 'R. Quinze de Novembro, 358 - Centro, São Paulo - SP', 
 ST_SetSRID(ST_MakePoint(-46.6389, -23.5456), 4326), 
 '(11) 3107-5432', null, '@outs15',
 '{"qui-sab": "20:00-04:00"}', 2, true, true);

-- Inserir badges do sistema
INSERT INTO badges (name, description, icon_url, criteria) VALUES
('Explorador Iniciante', 'Visitou sua primeira experiência no Taiglo', '/badges/explorer-beginner.svg', '{"visits": 1}'),
('Crítico Gastronômico', 'Avaliou 10 restaurantes diferentes', '/badges/food-critic.svg', '{"restaurant_reviews": 10}'),
('Caçador de Gems', 'Descobriu 5 lugares marcados como "hidden gems"', '/badges/gem-hunter.svg', '{"hidden_gems": 5}'),
('Local Guide', 'Adicionou 3 novos lugares ao Taiglo', '/badges/local-guide.svg', '{"places_added": 3}'),
('Café Expert', 'Visitou 15 cafés diferentes', '/badges/coffee-expert.svg', '{"cafe_visits": 15}'),
('Noturno', 'Visitou 10 bares ou casas noturnas', '/badges/nightlife.svg', '{"nightlife_visits": 10}'),
('Culturalista', 'Visitou 8 museus ou galerias', '/badges/culture.svg', '{"culture_visits": 8}'),
('Aventureiro Verde', 'Visitou 5 parques diferentes', '/badges/nature.svg', '{"park_visits": 5}');

-- Criar usuário de teste
INSERT INTO users (email, password_hash, first_name, last_name, bio, is_local_guide) VALUES
('teste@taiglo.com', '$2b$10$rOzJqQZ8kVx.QxMxQxMxQx', 'João', 'Silva', 'Apaixonado por descobrir lugares únicos em São Paulo', true);

-- Inserir algumas avaliações de exemplo
INSERT INTO reviews (experience_id, user_id, rating, title, content, visit_date) VALUES
((SELECT id FROM experiences WHERE name = 'Coffee Lab'), 
 (SELECT id FROM users WHERE email = 'teste@taiglo.com'), 
 5, 'Café excepcional!', 'Ambiente acolhedor e café de qualidade superior. O barista é muito conhecedor e faz recomendações excelentes.', '2024-01-15'),

((SELECT id FROM experiences WHERE name = 'Mocotó'), 
 (SELECT id FROM users WHERE email = 'teste@taiglo.com'), 
 5, 'Autêntica culinária nordestina', 'Experiência incrível! Comida saborosa, ambiente familiar e preço justo. O baião de dois é imperdível.', '2024-01-20'),

((SELECT id FROM experiences WHERE name = 'Bar do Luiz Fernandes'), 
 (SELECT id FROM users WHERE email = 'teste@taiglo.com'), 
 4, 'Boteco raiz', 'Lugar autêntico com petiscos caseiros. Ambiente simples mas com muito charme paulistano.', '2024-01-25');

