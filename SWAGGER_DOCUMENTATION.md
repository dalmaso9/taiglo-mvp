# Documentação Swagger UI - Taiglo MVP

## 📚 Visão Geral

O Flasgger foi configurado em todos os serviços do Taiglo MVP para fornecer documentação automática da API através do Swagger UI. Cada serviço possui sua própria documentação acessível através de uma interface web interativa.

## 🔗 URLs de Acesso

### 1. **API Gateway** (Porta 3000)
```
http://localhost:3000/apidocs/
```
- Documentação completa de todas as rotas do gateway
- Inclui autenticação JWT
- Rotas organizadas por tags: Authentication, Users, Experiences, Categories, Reviews, Search

### 2. **User Service** (Porta 3001)
```
http://localhost:3001/apidocs/
```
- Documentação das rotas de usuário e autenticação
- Inclui configuração de segurança JWT

### 3. **Experience Service** (Porta 3002)
```
http://localhost:3002/apidocs/
```
- Documentação das rotas de experiências e categorias

### 4. **Review Service** (Porta 3004)
```
http://localhost:3004/apidocs/
```
- Documentação das rotas de reviews

## 🚀 Como Usar

### 1. **Iniciar os Serviços**
```bash
# Usando Docker Compose
docker-compose up

# Ou individualmente
cd api-gateway && python src/main.py
cd user-service && python src/main.py
cd experience-service && python src/main.py
cd review-service && python src/main.py
```

### 2. **Acessar a Documentação**
1. Abra seu navegador
2. Acesse uma das URLs listadas acima
3. Explore as rotas disponíveis
4. Teste as APIs diretamente na interface

## 🔐 Autenticação

### Para rotas protegidas:
1. Faça login usando a rota `/api/auth/login`
2. Copie o token JWT retornado
3. Clique no botão "Authorize" no Swagger UI
4. Cole o token no formato: `Bearer <seu_token>`
5. Agora você pode testar rotas protegidas

## 📋 Funcionalidades do Swagger UI

### ✅ **Recursos Disponíveis:**
- **Documentação Interativa**: Teste APIs diretamente na interface
- **Esquemas de Dados**: Visualize estruturas de request/response
- **Códigos de Status**: Documentação completa de respostas
- **Parâmetros**: Descrição detalhada de parâmetros de entrada
- **Autenticação**: Suporte a JWT Bearer tokens
- **Tags**: Organização por categorias de endpoints

### 🏷️ **Tags Organizadas:**

#### API Gateway:
- **Authentication**: Login, registro, refresh de tokens
- **Users**: Gerenciamento de usuários
- **Experiences**: CRUD de experiências
- **Categories**: Gerenciamento de categorias
- **Reviews**: CRUD de reviews
- **Search**: Busca unificada

## 🔧 Configuração Técnica

### **Arquivos Modificados:**
- `src/main.py` em cada serviço
- `src/routes/gateway.py` no API Gateway
- `requirements.txt` em todos os serviços

### **Dependências Adicionadas:**
```python
flasgger==0.9.7.1
```

### **Configuração Swagger:**
```python
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}
```

## 📝 Exemplo de Uso

### 1. **Registrar um Usuário:**
```bash
POST /api/auth/register
{
    "username": "usuario_teste",
    "email": "teste@email.com",
    "password": "senha123"
}
```

### 2. **Fazer Login:**
```bash
POST /api/auth/login
{
    "email": "teste@email.com",
    "password": "senha123"
}
```

### 3. **Criar uma Experiência:**
```bash
POST /api/experiences
Authorization: Bearer <seu_token>
{
    "title": "Restaurante Incrível",
    "description": "Melhor comida da cidade",
    "category_id": 1,
    "latitude": -23.5505,
    "longitude": -46.6333,
    "address": "Rua das Flores, 123"
}
```

## 🎯 Benefícios

1. **Documentação Automática**: Sempre atualizada com o código
2. **Teste Interativo**: Teste APIs sem ferramentas externas
3. **Onboarding Rápido**: Novos desenvolvedores podem entender a API rapidamente
4. **Validação**: Esquemas JSON para validação de dados
5. **Colaboração**: Interface visual para discussão de APIs

## 🐛 Troubleshooting

### **Problema**: Swagger UI não carrega
**Solução**: Verifique se o serviço está rodando e acesse a URL correta

### **Problema**: Erro de CORS
**Solução**: O CORS já está configurado em todos os serviços

### **Problema**: Token não funciona
**Solução**: Certifique-se de usar o formato `Bearer <token>` no campo Authorization

## 📞 Suporte

Para dúvidas ou problemas com a documentação Swagger:
- Verifique os logs do serviço
- Confirme se todas as dependências estão instaladas
- Teste acessando diretamente a URL do Swagger UI

---

**🎉 Agora você tem documentação completa e interativa de todas as APIs do Taiglo MVP!**
