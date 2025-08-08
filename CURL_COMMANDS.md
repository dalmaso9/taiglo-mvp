# Taiglo MVP - Comandos cURL para Teste

Este arquivo contém exemplos de comandos cURL para testar todas as APIs do Taiglo MVP.

**Base URL:** `http://localhost:3000/api`

## Variáveis de Ambiente

Para facilitar os testes, defina estas variáveis:

```bash
export TAIGLO_BASE_URL="http://localhost:3000/api"
export JWT_TOKEN=""  # Será preenchido após login
export USER_ID=""    # Será preenchido após registro/login
export EXPERIENCE_ID=""  # Será preenchido após criar experiência
export REVIEW_ID=""  # Será preenchido após criar review
```

---

## 1. Autenticação e Usuários

### 1.1 Registrar Usuário

```bash
curl -X POST "${TAIGLO_BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@taiglo.com",
    "password": "senha123",
    "first_name": "João",
    "last_name": "Silva",
    "phone": "(11) 99999-9999",
    "bio": "Apaixonado por descobrir lugares únicos em São Paulo"
  }'
```

**Salvar o token retornado:**
```bash
export JWT_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
export USER_ID="uuid-do-usuario"
```

### 1.2 Login

```bash
curl -X POST "${TAIGLO_BASE_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@taiglo.com",
    "password": "senha123"
  }'
```

### 1.3 Obter Usuário Atual

```bash
curl -X GET "${TAIGLO_BASE_URL}/auth/me" \
  -H "Authorization: Bearer ${JWT_TOKEN}"
```

### 1.4 Atualizar Perfil

```bash
curl -X PUT "${TAIGLO_BASE_URL}/users/profile" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -d '{
    "first_name": "João Carlos",
    "last_name": "Silva Santos",
    "phone": "(11) 88888-8888",
    "bio": "Explorador urbano e foodie",
    "date_of_birth": "1990-05-15",
    "preferences": {
      "favorite_categories": ["cafes", "restaurants"],
      "price_range": [2, 4]
    }
  }'
```

### 1.5 Listar Usuários

```bash
curl -X GET "${TAIGLO_BASE_URL}/users?page=1&per_page=10"
```

### 1.6 Buscar Usuários

```bash
curl -X GET "${TAIGLO_BASE_URL}/users/search?q=João&page=1&per_page=5"
```

---

## 2. Categorias

### 2.1 Listar Categorias

```bash
curl -X GET "${TAIGLO_BASE_URL}/categories"
```

### 2.2 Obter Categoria Específica

```bash
# Primeiro, obter ID de uma categoria da listagem acima
export CATEGORY_ID="uuid-categoria"

curl -X GET "${TAIGLO_BASE_URL}/categories/${CATEGORY_ID}"
```

### 2.3 Criar Nova Categoria

```bash
curl -X POST "${TAIGLO_BASE_URL}/categories" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Padarias",
    "description": "Padarias artesanais e confeitarias especiais",
    "icon_url": "/icons/bakery.svg",
    "color_hex": "#D2691E"
  }'
```

### 2.4 Atualizar Categoria

```bash
curl -X PUT "${TAIGLO_BASE_URL}/categories/${CATEGORY_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Padarias Artesanais",
    "description": "Padarias artesanais, confeitarias e docerias especiais"
  }'
```

---

## 3. Experiências

### 3.1 Listar Experiências

```bash
curl -X GET "${TAIGLO_BASE_URL}/experiences?page=1&per_page=10"
```

### 3.2 Listar Experiências com Filtros

```bash
# Filtrar por categoria e rating mínimo
curl -X GET "${TAIGLO_BASE_URL}/experiences?category_id=${CATEGORY_ID}&min_rating=4.0&sort_by=rating&sort_order=desc"

# Buscar por texto
curl -X GET "${TAIGLO_BASE_URL}/experiences?search=café&page=1&per_page=5"

# Filtrar gems escondidas
curl -X GET "${TAIGLO_BASE_URL}/experiences?is_hidden_gem=true&sort_by=rating&sort_order=desc"
```

### 3.3 Buscar Experiências Próximas

```bash
# Buscar em um raio de 2km da Vila Madalena
curl -X GET "${TAIGLO_BASE_URL}/experiences/nearby?latitude=-23.5618&longitude=-46.6918&radius_km=2&limit=20"

# Buscar cafés próximos
curl -X GET "${TAIGLO_BASE_URL}/experiences/nearby?latitude=-23.5618&longitude=-46.6918&radius_km=5&category_id=${CATEGORY_ID}&min_rating=4.0"
```

### 3.4 Obter Experiência Específica

```bash
# Primeiro, obter ID de uma experiência da listagem acima
export EXPERIENCE_ID="uuid-experiencia"

curl -X GET "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}"
```

### 3.5 Criar Nova Experiência

```bash
curl -X POST "${TAIGLO_BASE_URL}/experiences" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Teste API",
    "description": "Um café criado via API para testar o sistema",
    "category_id": "'${CATEGORY_ID}'",
    "address": "R. Augusta, 1234 - Consolação, São Paulo - SP",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "phone": "(11) 3333-4444",
    "website_url": "https://cafeteste.com.br",
    "instagram_handle": "@cafeteste_sp",
    "opening_hours": {
      "seg-sex": "07:00-18:00",
      "sab-dom": "08:00-17:00"
    },
    "price_range": 2,
    "is_hidden_gem": true,
    "created_by": "'${USER_ID}'"
  }'
```

### 3.6 Atualizar Experiência

```bash
curl -X PUT "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Teste API - Atualizado",
    "description": "Um café criado via API para testar o sistema - versão atualizada",
    "phone": "(11) 3333-5555",
    "price_range": 3,
    "opening_hours": {
      "seg-sex": "06:30-19:00",
      "sab": "07:00-18:00",
      "dom": "08:00-17:00"
    }
  }'
```

### 3.7 Deletar Experiência

```bash
curl -X DELETE "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}"
```

---

## 4. Avaliações (Reviews)

### 4.1 Listar Avaliações

```bash
curl -X GET "${TAIGLO_BASE_URL}/reviews?page=1&per_page=10"
```

### 4.2 Listar Avaliações de uma Experiência

```bash
curl -X GET "${TAIGLO_BASE_URL}/reviews?experience_id=${EXPERIENCE_ID}&include_user_info=true&sort_by=helpful_votes&sort_order=desc"
```

### 4.3 Listar Avaliações de um Usuário

```bash
curl -X GET "${TAIGLO_BASE_URL}/reviews?user_id=${USER_ID}&sort_by=created_at&sort_order=desc"
```

### 4.4 Filtrar Avaliações por Rating

```bash
curl -X GET "${TAIGLO_BASE_URL}/reviews?min_rating=4&max_rating=5&sort_by=rating&sort_order=desc"
```

### 4.5 Obter Avaliação Específica

```bash
# Primeiro, obter ID de uma review da listagem acima
export REVIEW_ID="uuid-review"

curl -X GET "${TAIGLO_BASE_URL}/reviews/${REVIEW_ID}?include_user_info=true"
```

### 4.6 Criar Nova Avaliação

```bash
curl -X POST "${TAIGLO_BASE_URL}/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "experience_id": "'${EXPERIENCE_ID}'",
    "user_id": "'${USER_ID}'",
    "rating": 5,
    "title": "Experiência incrível via API!",
    "content": "Testei este lugar através da API e foi uma experiência fantástica. O café estava delicioso, o atendimento foi excepcional e o ambiente muito aconchegante. Recomendo fortemente para quem busca um lugar especial para relaxar.",
    "photos": [
      "https://exemplo.com/foto1.jpg",
      "https://exemplo.com/foto2.jpg"
    ],
    "visit_date": "2024-01-14"
  }'
```

### 4.7 Atualizar Avaliação

```bash
curl -X PUT "${TAIGLO_BASE_URL}/reviews/${REVIEW_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4,
    "title": "Experiência muito boa - Atualizada",
    "content": "Após uma segunda visita, mantenho minha avaliação positiva, mas com algumas ressalvas. O café continua excelente, mas o atendimento estava um pouco mais lento desta vez.",
    "photos": [
      "https://exemplo.com/foto1.jpg",
      "https://exemplo.com/foto2.jpg",
      "https://exemplo.com/foto3.jpg"
    ]
  }'
```

### 4.8 Votar se Review é Útil

```bash
curl -X POST "${TAIGLO_BASE_URL}/reviews/${REVIEW_ID}/helpful" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "'${USER_ID}'",
    "is_helpful": true
  }'
```

### 4.9 Obter Estatísticas de Reviews de uma Experiência

```bash
curl -X GET "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}/reviews/stats"
```

### 4.10 Deletar Avaliação

```bash
curl -X DELETE "${TAIGLO_BASE_URL}/reviews/${REVIEW_ID}"
```

---

## 5. Rotas Combinadas

### 5.1 Experiência Completa (com Reviews e Stats)

```bash
curl -X GET "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}/full"
```

### 5.2 Busca Unificada

```bash
curl -X GET "${TAIGLO_BASE_URL}/search?q=café"
```

---

## 6. Monitoramento

### 6.1 Health Check do Gateway

```bash
curl -X GET "http://localhost:3000/health"
```

### 6.2 Health Check de Todos os Serviços

```bash
curl -X GET "http://localhost:3000/services/health"
```

### 6.3 Health Check de Serviços Individuais

```bash
# User Service
curl -X GET "http://user-service:3001/health"

# Experience Service
curl -X GET "http://experience-service:3002/health"

# Review Service
curl -X GET "http://review-service:3004/health"
```

---

## Scripts de Teste Automatizado

### Teste Completo do Fluxo

```bash
#!/bin/bash

# Configurar variáveis
export TAIGLO_BASE_URL="http://localhost:3000/api"

echo "=== Testando Fluxo Completo do Taiglo MVP ==="

# 1. Registrar usuário
echo "1. Registrando usuário..."
REGISTER_RESPONSE=$(curl -s -X POST "${TAIGLO_BASE_URL}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste'$(date +%s)'@taiglo.com",
    "password": "senha123",
    "first_name": "João",
    "last_name": "Silva",
    "phone": "(11) 99999-9999"
  }')

export JWT_TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
export USER_ID=$(echo $REGISTER_RESPONSE | jq -r '.user.id')

echo "✓ Usuário registrado. ID: $USER_ID"

# 2. Listar categorias
echo "2. Listando categorias..."
CATEGORIES_RESPONSE=$(curl -s -X GET "${TAIGLO_BASE_URL}/categories")
export CATEGORY_ID=$(echo $CATEGORIES_RESPONSE | jq -r '.categories[0].id')

echo "✓ Categorias listadas. Usando categoria: $CATEGORY_ID"

# 3. Criar experiência
echo "3. Criando experiência..."
EXPERIENCE_RESPONSE=$(curl -s -X POST "${TAIGLO_BASE_URL}/experiences" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Teste Automatizado",
    "description": "Café criado automaticamente para teste",
    "category_id": "'${CATEGORY_ID}'",
    "address": "R. Teste, 123 - São Paulo - SP",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "price_range": 2,
    "created_by": "'${USER_ID}'"
  }')

export EXPERIENCE_ID=$(echo $EXPERIENCE_RESPONSE | jq -r '.experience.id')

echo "✓ Experiência criada. ID: $EXPERIENCE_ID"

# 4. Buscar experiências próximas
echo "4. Buscando experiências próximas..."
curl -s -X GET "${TAIGLO_BASE_URL}/experiences/nearby?latitude=-23.5505&longitude=-46.6333&radius_km=5" | jq '.total_found'

echo "✓ Busca por proximidade realizada"

# 5. Criar avaliação
echo "5. Criando avaliação..."
REVIEW_RESPONSE=$(curl -s -X POST "${TAIGLO_BASE_URL}/reviews" \
  -H "Content-Type: application/json" \
  -d '{
    "experience_id": "'${EXPERIENCE_ID}'",
    "user_id": "'${USER_ID}'",
    "rating": 5,
    "title": "Teste automatizado",
    "content": "Esta é uma avaliação criada automaticamente para teste do sistema.",
    "visit_date": "2024-01-15"
  }')

export REVIEW_ID=$(echo $REVIEW_RESPONSE | jq -r '.review.id')

echo "✓ Avaliação criada. ID: $REVIEW_ID"

# 6. Obter experiência completa
echo "6. Obtendo experiência completa..."
curl -s -X GET "${TAIGLO_BASE_URL}/experiences/${EXPERIENCE_ID}/full" | jq '.experience.name'

echo "✓ Experiência completa obtida"

# 7. Verificar health dos serviços
echo "7. Verificando health dos serviços..."
curl -s -X GET "http://localhost:3000/services/health" | jq '.overall_status'

echo "✓ Health check realizado"

echo "=== Teste completo finalizado com sucesso! ==="
```

### Teste de Performance

```bash
#!/bin/bash

echo "=== Teste de Performance - Busca por Proximidade ==="

# Fazer 10 requisições simultâneas
for i in {1..10}; do
  (
    time curl -s -X GET "${TAIGLO_BASE_URL}/experiences/nearby?latitude=-23.5618&longitude=-46.6918&radius_km=5" > /dev/null
  ) &
done

wait
echo "✓ 10 requisições simultâneas completadas"
```

---

## Troubleshooting

### Problemas Comuns

1. **Erro 401 - Token inválido:**
   ```bash
   # Fazer login novamente
   curl -X POST "${TAIGLO_BASE_URL}/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "seu@email.com", "password": "suasenha"}'
   ```

2. **Erro 404 - Serviço não encontrado:**
   ```bash
   # Verificar se os serviços estão rodando
   curl -X GET "http://localhost:3000/services/health"
   ```

3. **Erro de conexão:**
   ```bash
   # Verificar se o API Gateway está rodando
   curl -X GET "http://localhost:3000/health"
   ```

### Comandos de Debug

```bash
# Ver logs detalhados com verbose
curl -v -X GET "${TAIGLO_BASE_URL}/experiences"

# Salvar resposta em arquivo
curl -X GET "${TAIGLO_BASE_URL}/experiences" -o experiences.json

# Mostrar apenas headers da resposta
curl -I -X GET "${TAIGLO_BASE_URL}/experiences"

# Medir tempo de resposta
curl -w "@curl-format.txt" -X GET "${TAIGLO_BASE_URL}/experiences" -o /dev/null -s
```

Arquivo `curl-format.txt`:
```
     time_namelookup:  %{time_namelookup}\n
        time_connect:  %{time_connect}\n
     time_appconnect:  %{time_appconnect}\n
    time_pretransfer:  %{time_pretransfer}\n
       time_redirect:  %{time_redirect}\n
  time_starttransfer:  %{time_starttransfer}\n
                     ----------\n
          time_total:  %{time_total}\n
```

