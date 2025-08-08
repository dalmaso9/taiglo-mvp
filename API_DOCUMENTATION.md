# Taiglo MVP - Documentação das APIs

## Visão Geral

O Taiglo MVP é composto por microsserviços que se comunicam através de um API Gateway centralizado. Todas as requisições devem ser feitas através do gateway na porta 3000.

**Base URL:** `http://localhost:3000/api`

## Arquitetura dos Serviços

- **API Gateway** (Porta 3000): Ponto de entrada único para todas as requisições
- **User Service** (Porta 3001): Gerenciamento de usuários e autenticação
- **Experience Service** (Porta 3002): CRUD de experiências e busca geoespacial
- **Review Service** (Porta 3004): Sistema de avaliações e moderação

## Autenticação

O sistema utiliza JWT (JSON Web Tokens) para autenticação. Após o login, inclua o token no header das requisições autenticadas:

```
Authorization: Bearer <seu_jwt_token>
```

## Status Codes

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Erro de validação
- `401` - Não autorizado
- `404` - Não encontrado
- `409` - Conflito (ex: email já existe)
- `500` - Erro interno do servidor

---

## 1. Autenticação e Usuários

### 1.1 Registrar Usuário

**POST** `/api/auth/register`

Cria uma nova conta de usuário.

**Body:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "minhasenha123",
  "first_name": "João",
  "last_name": "Silva",
  "phone": "(11) 99999-9999",
  "bio": "Apaixonado por descobrir lugares únicos em São Paulo"
}
```

**Response (201):**
```json
{
  "message": "Usuário criado com sucesso",
  "user": {
    "id": "uuid-do-usuario",
    "email": "usuario@exemplo.com",
    "first_name": "João",
    "last_name": "Silva",
    "phone": "(11) 99999-9999",
    "bio": "Apaixonado por descobrir lugares únicos em São Paulo",
    "is_verified": false,
    "is_local_guide": false,
    "preferences": {},
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 1.2 Login

**POST** `/api/auth/login`

Autentica um usuário existente.

**Body:**
```json
{
  "email": "usuario@exemplo.com",
  "password": "minhasenha123"
}
```

**Response (200):**
```json
{
  "message": "Login realizado com sucesso",
  "user": {
    "id": "uuid-do-usuario",
    "email": "usuario@exemplo.com",
    "first_name": "João",
    "last_name": "Silva",
    "is_verified": false,
    "is_local_guide": false
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 1.3 Obter Usuário Atual

**GET** `/api/auth/me`

Retorna informações do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200):**
```json
{
  "user": {
    "id": "uuid-do-usuario",
    "email": "usuario@exemplo.com",
    "first_name": "João",
    "last_name": "Silva",
    "phone": "(11) 99999-9999",
    "bio": "Apaixonado por descobrir lugares únicos em São Paulo",
    "is_verified": false,
    "is_local_guide": false,
    "preferences": {},
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 1.4 Atualizar Perfil

**PUT** `/api/users/profile`

Atualiza o perfil do usuário autenticado.

**Headers:**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
  "first_name": "João Carlos",
  "last_name": "Silva Santos",
  "phone": "(11) 88888-8888",
  "bio": "Explorador urbano e foodie",
  "date_of_birth": "1990-05-15",
  "preferences": {
    "favorite_categories": ["cafes", "restaurants"],
    "price_range": [2, 4]
  }
}
```

**Response (200):**
```json
{
  "message": "Perfil atualizado com sucesso",
  "user": {
    "id": "uuid-do-usuario",
    "email": "usuario@exemplo.com",
    "first_name": "João Carlos",
    "last_name": "Silva Santos",
    "phone": "(11) 88888-8888",
    "bio": "Explorador urbano e foodie",
    "date_of_birth": "1990-05-15",
    "preferences": {
      "favorite_categories": ["cafes", "restaurants"],
      "price_range": [2, 4]
    },
    "updated_at": "2024-01-15T11:45:00"
  }
}
```

---

## 2. Categorias de Experiências

### 2.1 Listar Categorias

**GET** `/api/categories`

Retorna todas as categorias de experiências disponíveis.

**Response (200):**
```json
{
  "categories": [
    {
      "id": "uuid-categoria",
      "name": "Cafés",
      "description": "Cafeterias e casas de café especiais",
      "icon_url": "/icons/coffee.svg",
      "color_hex": "#8B4513",
      "created_at": "2024-01-01T00:00:00",
      "experience_count": 5
    },
    {
      "id": "uuid-categoria-2",
      "name": "Restaurantes",
      "description": "Restaurantes e bistrôs únicos",
      "icon_url": "/icons/restaurant.svg",
      "color_hex": "#FF6B35",
      "created_at": "2024-01-01T00:00:00",
      "experience_count": 8
    }
  ],
  "total": 8
}
```

### 2.2 Obter Categoria Específica

**GET** `/api/categories/{category_id}`

Retorna detalhes de uma categoria específica.

**Response (200):**
```json
{
  "category": {
    "id": "uuid-categoria",
    "name": "Cafés",
    "description": "Cafeterias e casas de café especiais",
    "icon_url": "/icons/coffee.svg",
    "color_hex": "#8B4513",
    "created_at": "2024-01-01T00:00:00",
    "experience_count": 5
  }
}
```

---

## 3. Experiências

### 3.1 Listar Experiências

**GET** `/api/experiences`

Lista experiências com filtros e paginação.

**Query Parameters:**
- `page` (int): Página (padrão: 1)
- `per_page` (int): Itens por página (padrão: 20, máximo: 100)
- `category_id` (string): Filtrar por categoria
- `is_hidden_gem` (boolean): Filtrar gems escondidas
- `min_rating` (float): Rating mínimo
- `price_range` (int): Faixa de preço (1-4)
- `search` (string): Buscar por nome, descrição ou endereço
- `sort_by` (string): Ordenar por `created_at`, `rating`, `name`
- `sort_order` (string): `asc` ou `desc`

**Exemplo:** `/api/experiences?category_id=uuid-cafe&min_rating=4.0&sort_by=rating&sort_order=desc`

**Response (200):**
```json
{
  "experiences": [
    {
      "id": "uuid-experiencia",
      "name": "Coffee Lab",
      "description": "Café de especialidade com grãos selecionados e ambiente acolhedor no coração de Pinheiros",
      "category_id": "uuid-categoria-cafe",
      "category": {
        "id": "uuid-categoria-cafe",
        "name": "Cafés",
        "color_hex": "#8B4513"
      },
      "address": "R. Fradique Coutinho, 1340 - Vila Madalena, São Paulo - SP",
      "coordinates": {
        "latitude": -23.5618,
        "longitude": -46.6918
      },
      "phone": "(11) 3031-5555",
      "website_url": "https://coffeelab.com.br",
      "instagram_handle": "@coffeelab_sp",
      "opening_hours": {
        "seg-sex": "07:00-19:00",
        "sab": "08:00-18:00",
        "dom": "08:00-17:00"
      },
      "price_range": 3,
      "average_rating": 4.5,
      "total_reviews": 12,
      "is_hidden_gem": true,
      "is_verified": true,
      "authenticity_score": 0.85,
      "created_by": "uuid-usuario-criador",
      "created_at": "2024-01-10T09:00:00",
      "updated_at": "2024-01-15T14:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 3,
    "per_page": 20,
    "total": 45,
    "has_next": true,
    "has_prev": false
  },
  "filters": {
    "category_id": "uuid-cafe",
    "min_rating": 4.0,
    "sort_by": "rating",
    "sort_order": "desc"
  }
}
```

### 3.2 Buscar Experiências Próximas

**GET** `/api/experiences/nearby`

Busca experiências próximas a uma coordenada específica.

**Query Parameters (Obrigatórios):**
- `latitude` (float): Latitude da localização
- `longitude` (float): Longitude da localização

**Query Parameters (Opcionais):**
- `radius_km` (float): Raio de busca em km (padrão: 5, máximo: 50)
- `limit` (int): Limite de resultados (padrão: 50, máximo: 100)
- `category_id` (string): Filtrar por categoria
- `min_rating` (float): Rating mínimo

**Exemplo:** `/api/experiences/nearby?latitude=-23.5618&longitude=-46.6918&radius_km=2&category_id=uuid-cafe`

**Response (200):**
```json
{
  "experiences": [
    {
      "id": "uuid-experiencia",
      "name": "Coffee Lab",
      "description": "Café de especialidade com grãos selecionados...",
      "coordinates": {
        "latitude": -23.5618,
        "longitude": -46.6918
      },
      "distance_km": 0.15,
      "average_rating": 4.5,
      "price_range": 3,
      "is_hidden_gem": true
    }
  ],
  "search_params": {
    "latitude": -23.5618,
    "longitude": -46.6918,
    "radius_km": 2,
    "category_id": "uuid-cafe"
  },
  "total_found": 8
}
```

### 3.3 Obter Experiência Específica

**GET** `/api/experiences/{experience_id}`

Retorna detalhes completos de uma experiência.

**Response (200):**
```json
{
  "experience": {
    "id": "uuid-experiencia",
    "name": "Coffee Lab",
    "description": "Café de especialidade com grãos selecionados e ambiente acolhedor no coração de Pinheiros",
    "category": {
      "id": "uuid-categoria-cafe",
      "name": "Cafés",
      "description": "Cafeterias e casas de café especiais",
      "color_hex": "#8B4513"
    },
    "address": "R. Fradique Coutinho, 1340 - Vila Madalena, São Paulo - SP",
    "coordinates": {
      "latitude": -23.5618,
      "longitude": -46.6918
    },
    "phone": "(11) 3031-5555",
    "website_url": "https://coffeelab.com.br",
    "instagram_handle": "@coffeelab_sp",
    "opening_hours": {
      "seg-sex": "07:00-19:00",
      "sab": "08:00-18:00",
      "dom": "08:00-17:00"
    },
    "price_range": 3,
    "average_rating": 4.5,
    "total_reviews": 12,
    "is_hidden_gem": true,
    "is_verified": true,
    "authenticity_score": 0.85,
    "created_at": "2024-01-10T09:00:00",
    "updated_at": "2024-01-15T14:30:00"
  }
}
```

### 3.4 Criar Nova Experiência

**POST** `/api/experiences`

Cria uma nova experiência.

**Body:**
```json
{
  "name": "Novo Café Especial",
  "description": "Um café aconchegante com torrefação própria e ambiente descontraído",
  "category_id": "uuid-categoria-cafe",
  "address": "R. Augusta, 1234 - Consolação, São Paulo - SP",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "phone": "(11) 3333-4444",
  "website_url": "https://novocafe.com.br",
  "instagram_handle": "@novocafe_sp",
  "opening_hours": {
    "seg-sex": "07:00-18:00",
    "sab-dom": "08:00-17:00"
  },
  "price_range": 2,
  "is_hidden_gem": true,
  "created_by": "uuid-usuario"
}
```

**Response (201):**
```json
{
  "message": "Experiência criada com sucesso",
  "experience": {
    "id": "uuid-nova-experiencia",
    "name": "Novo Café Especial",
    "description": "Um café aconchegante com torrefação própria e ambiente descontraído",
    "category_id": "uuid-categoria-cafe",
    "address": "R. Augusta, 1234 - Consolação, São Paulo - SP",
    "coordinates": {
      "latitude": -23.5505,
      "longitude": -46.6333
    },
    "phone": "(11) 3333-4444",
    "website_url": "https://novocafe.com.br",
    "instagram_handle": "@novocafe_sp",
    "opening_hours": {
      "seg-sex": "07:00-18:00",
      "sab-dom": "08:00-17:00"
    },
    "price_range": 2,
    "average_rating": 0.0,
    "total_reviews": 0,
    "is_hidden_gem": true,
    "is_verified": false,
    "authenticity_score": 0.0,
    "created_by": "uuid-usuario",
    "created_at": "2024-01-15T16:20:00",
    "updated_at": "2024-01-15T16:20:00"
  }
}
```

---

## 4. Avaliações (Reviews)

### 4.1 Listar Avaliações

**GET** `/api/reviews`

Lista avaliações com filtros e paginação.

**Query Parameters:**
- `page` (int): Página (padrão: 1)
- `per_page` (int): Itens por página (padrão: 20, máximo: 100)
- `experience_id` (string): Filtrar por experiência
- `user_id` (string): Filtrar por usuário
- `min_rating` (int): Rating mínimo (1-5)
- `max_rating` (int): Rating máximo (1-5)
- `is_verified` (boolean): Filtrar reviews verificadas
- `include_user_info` (boolean): Incluir informações do usuário
- `sort_by` (string): Ordenar por `created_at`, `rating`, `helpful_votes`
- `sort_order` (string): `asc` ou `desc`

**Exemplo:** `/api/reviews?experience_id=uuid-experiencia&include_user_info=true&sort_by=helpful_votes&sort_order=desc`

**Response (200):**
```json
{
  "reviews": [
    {
      "id": "uuid-review",
      "experience_id": "uuid-experiencia",
      "user_id": "uuid-usuario",
      "rating": 5,
      "title": "Café excepcional!",
      "content": "Ambiente acolhedor e café de qualidade superior. O barista é muito conhecedor e faz recomendações excelentes.",
      "photos": [
        "https://exemplo.com/foto1.jpg",
        "https://exemplo.com/foto2.jpg"
      ],
      "visit_date": "2024-01-15",
      "is_verified": false,
      "authenticity_score": 0.75,
      "helpful_votes": 8,
      "created_at": "2024-01-15T18:30:00",
      "updated_at": "2024-01-15T18:30:00",
      "user": {
        "id": "uuid-usuario",
        "first_name": "João",
        "last_name": "Silva",
        "is_local_guide": true
      }
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 2,
    "per_page": 20,
    "total": 25,
    "has_next": true,
    "has_prev": false
  }
}
```

### 4.2 Criar Avaliação

**POST** `/api/reviews`

Cria uma nova avaliação para uma experiência.

**Body:**
```json
{
  "experience_id": "uuid-experiencia",
  "user_id": "uuid-usuario",
  "rating": 5,
  "title": "Experiência incrível!",
  "content": "Lugar maravilhoso com atendimento excepcional. A comida estava deliciosa e o ambiente muito aconchegante. Recomendo fortemente!",
  "photos": [
    "https://exemplo.com/minha-foto1.jpg",
    "https://exemplo.com/minha-foto2.jpg"
  ],
  "visit_date": "2024-01-14"
}
```

**Response (201):**
```json
{
  "message": "Review criada com sucesso",
  "review": {
    "id": "uuid-nova-review",
    "experience_id": "uuid-experiencia",
    "user_id": "uuid-usuario",
    "rating": 5,
    "title": "Experiência incrível!",
    "content": "Lugar maravilhoso com atendimento excepcional. A comida estava deliciosa e o ambiente muito aconchegante. Recomendo fortemente!",
    "photos": [
      "https://exemplo.com/minha-foto1.jpg",
      "https://exemplo.com/minha-foto2.jpg"
    ],
    "visit_date": "2024-01-14",
    "is_verified": false,
    "authenticity_score": 0.8,
    "helpful_votes": 0,
    "created_at": "2024-01-15T19:45:00",
    "updated_at": "2024-01-15T19:45:00"
  }
}
```

### 4.3 Votar se Review é Útil

**POST** `/api/reviews/{review_id}/helpful`

Vota se uma review é útil ou não.

**Body:**
```json
{
  "user_id": "uuid-usuario-votante",
  "is_helpful": true
}
```

**Response (200):**
```json
{
  "message": "Voto registrado com sucesso",
  "helpful_votes": 9
}
```

### 4.4 Estatísticas de Reviews de uma Experiência

**GET** `/api/experiences/{experience_id}/reviews/stats`

Retorna estatísticas das avaliações de uma experiência.

**Response (200):**
```json
{
  "experience_id": "uuid-experiencia",
  "total_reviews": 15,
  "average_rating": 4.3,
  "rating_distribution": {
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 5,
    "5": 7
  },
  "verified_reviews": 3,
  "average_authenticity_score": 0.72
}
```

---

## 5. Rotas Combinadas

### 5.1 Experiência Completa

**GET** `/api/experiences/{experience_id}/full`

Retorna experiência com reviews e estatísticas em uma única requisição.

**Response (200):**
```json
{
  "experience": {
    "id": "uuid-experiencia",
    "name": "Coffee Lab",
    "description": "Café de especialidade...",
    "category": {...},
    "coordinates": {...},
    "average_rating": 4.5,
    "total_reviews": 12
  },
  "reviews": [
    {
      "id": "uuid-review",
      "rating": 5,
      "title": "Café excepcional!",
      "content": "Ambiente acolhedor...",
      "user": {
        "first_name": "João",
        "last_name": "Silva"
      }
    }
  ],
  "review_stats": {
    "total_reviews": 12,
    "average_rating": 4.5,
    "rating_distribution": {
      "1": 0, "2": 0, "3": 1, "4": 4, "5": 7
    }
  }
}
```

### 5.2 Busca Unificada

**GET** `/api/search`

Busca unificada em experiências.

**Query Parameters:**
- `q` (string, obrigatório): Termo de busca

**Exemplo:** `/api/search?q=café`

**Response (200):**
```json
{
  "query": "café",
  "experiences": [
    {
      "id": "uuid-experiencia",
      "name": "Coffee Lab",
      "description": "Café de especialidade...",
      "average_rating": 4.5,
      "coordinates": {
        "latitude": -23.5618,
        "longitude": -46.6918
      }
    }
  ],
  "total_found": 8
}
```

---

## 6. Monitoramento

### 6.1 Health Check do Gateway

**GET** `/health`

Verifica se o API Gateway está funcionando.

**Response (200):**
```json
{
  "status": "healthy",
  "service": "api-gateway"
}
```

### 6.2 Health Check de Todos os Serviços

**GET** `/services/health`

Verifica o status de todos os microsserviços.

**Response (200):**
```json
{
  "gateway_status": "healthy",
  "services": {
    "user-service": {
      "status": "healthy",
      "response_time": 0.045
    },
    "experience-service": {
      "status": "healthy",
      "response_time": 0.032
    },
    "review-service": {
      "status": "healthy",
      "response_time": 0.028
    }
  },
  "overall_status": "healthy"
}
```

---

## Códigos de Erro Comuns

### 400 - Bad Request
```json
{
  "error": "Campo email é obrigatório"
}
```

### 401 - Unauthorized
```json
{
  "error": "Token de acesso inválido ou expirado"
}
```

### 404 - Not Found
```json
{
  "error": "Experiência não encontrada"
}
```

### 409 - Conflict
```json
{
  "error": "Email já cadastrado"
}
```

### 500 - Internal Server Error
```json
{
  "error": "Erro interno do servidor"
}
```

---

## Próximos Passos

Esta documentação cobre as APIs essenciais do MVP. Funcionalidades futuras incluirão:

- Map Service para integração com mapas
- Sistema de recomendações baseado em ML
- Notificações push
- Analytics e métricas avançadas
- Sistema de badges e gamificação

