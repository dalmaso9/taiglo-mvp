# Taiglo MVP - Guia de Instalação e Setup

Este guia fornece instruções completas para configurar e executar o MVP do Taiglo localmente.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Docker** (versão 20.10 ou superior)
- **Docker Compose** (versão 2.0 ou superior)
- **Git** (para clonar o repositório)

### Verificar Instalação

```bash
# Verificar Docker
docker --version
docker-compose --version

# Verificar Git
git --version
```

## 🚀 Setup Rápido

### 1. Clonar/Baixar o Projeto

Se você recebeu o projeto como arquivo:
```bash
# Extrair e navegar para o diretório
cd taiglo-mvp
```

Se você tem acesso ao repositório:
```bash
git clone <repository-url>
cd taiglo-mvp
```

### 2. Iniciar Todos os Serviços

```bash
# Construir e iniciar todos os serviços
docker-compose up --build

# Ou em background (recomendado)
docker-compose up --build -d
```

### 3. Aguardar Inicialização

O sistema levará alguns minutos para:
- Baixar as imagens Docker necessárias
- Construir os serviços
- Inicializar o banco de dados PostgreSQL com PostGIS
- Popular o banco com dados de seed (20+ experiências de São Paulo)
- Iniciar todos os microsserviços

### 4. Verificar Status

```bash
# Verificar se todos os serviços estão rodando
docker-compose ps

# Verificar logs em tempo real
docker-compose logs -f

# Verificar logs de um serviço específico
docker-compose logs -f api-gateway
```

### 5. Acessar a Aplicação

- **Frontend (Interface Web):** http://localhost:5173
- **API Gateway:** http://localhost:3000
- **Documentação das APIs:** Consulte `API_DOCUMENTATION.md`

## 🔧 Serviços e Portas

| Serviço | Porta | URL | Descrição |
|---------|-------|-----|-----------|
| Frontend | 5173 | http://localhost:5173 | Interface web do Taiglo |
| API Gateway | 3000 | http://localhost:3000 | Gateway principal das APIs |
| User Service | 3001 | http://localhost:3001 | Serviço de usuários |
| Experience Service | 3002 | http://localhost:3002 | Serviço de experiências |
| Review Service | 3004 | http://localhost:3004 | Serviço de avaliações |
| PostgreSQL | 5432 | localhost:5432 | Banco de dados principal |
| Redis | 6379 | localhost:6379 | Cache e sessões |

## 🧪 Testando o Sistema

### Conta de Teste

Use estas credenciais para testar o sistema:
- **Email:** teste@taiglo.com
- **Senha:** senha123

### Health Checks

```bash
# Verificar saúde de todos os serviços
curl http://localhost:3000/services/health

# Verificar serviços individuais
curl http://user-service:3001/health  # User Service
curl http://experience-service:3002/health  # Experience Service
curl http://review-service:3004/health  # Review Service
```

### Teste das APIs

Consulte os arquivos:
- `CURL_COMMANDS.md` - Comandos cURL prontos para uso
- `POSTMAN_COLLECTION.json` - Coleção Postman para importar
- `API_DOCUMENTATION.md` - Documentação completa das APIs

## 🛠️ Comandos Úteis

### Gerenciamento dos Serviços

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (limpar dados)
docker-compose down -v

# Reiniciar um serviço específico
docker-compose restart api-gateway

# Ver logs de um serviço
docker-compose logs -f frontend

# Executar comando em um container
docker-compose exec postgres psql -U taiglo_user -d taiglo_db
```

### Desenvolvimento

```bash
# Reconstruir apenas um serviço
docker-compose build user-service

# Iniciar apenas alguns serviços
docker-compose up postgres redis api-gateway

# Escalar um serviço (múltiplas instâncias)
docker-compose up --scale experience-service=2
```

### Limpeza

```bash
# Remover containers parados
docker-compose down

# Remover imagens não utilizadas
docker image prune

# Limpeza completa (cuidado!)
docker system prune -a
```

## 🗄️ Banco de Dados

### Conexão Direta

```bash
# Conectar ao PostgreSQL
docker-compose exec postgres psql -U taiglo_user -d taiglo_db

# Ou usando cliente externo
psql -h localhost -p 5432 -U taiglo_user -d taiglo_db
```

### Estrutura do Banco

O banco é automaticamente criado com:
- **Extensão PostGIS** para dados geoespaciais
- **Tabelas principais:** users, categories, experiences, reviews
- **Dados de seed:** 20+ experiências reais de São Paulo
- **Índices otimizados** para consultas geoespaciais

### Backup e Restore

```bash
# Fazer backup
docker-compose exec postgres pg_dump -U taiglo_user taiglo_db > backup.sql

# Restaurar backup
docker-compose exec -T postgres psql -U taiglo_user -d taiglo_db < backup.sql
```

## 🔍 Troubleshooting

### Problemas Comuns

#### 1. Porta já em uso
```bash
# Verificar quais portas estão em uso
netstat -tulpn | grep :5173
netstat -tulpn | grep :3000

# Parar processos que estão usando as portas
sudo lsof -ti:5173 | xargs kill -9
```

#### 2. Erro de permissão no Docker
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Reiniciar sessão ou executar
newgrp docker
```

#### 3. Banco de dados não inicializa
```bash
# Verificar logs do PostgreSQL
docker-compose logs postgres

# Remover volume e recriar
docker-compose down -v
docker-compose up postgres
```

#### 4. Serviços não conseguem se conectar
```bash
# Verificar rede Docker
docker network ls
docker network inspect taiglo-mvp_taiglo_network

# Reiniciar todos os serviços
docker-compose down && docker-compose up
```

#### 5. Frontend não carrega
```bash
# Verificar se o API Gateway está rodando
curl http://localhost:3000/health

# Verificar logs do frontend
docker-compose logs frontend

# Reconstruir o frontend
docker-compose build frontend
docker-compose up frontend
```

### Logs Detalhados

```bash
# Ver todos os logs
docker-compose logs

# Logs em tempo real
docker-compose logs -f

# Logs de um serviço específico
docker-compose logs -f api-gateway

# Logs com timestamp
docker-compose logs -t
```

### Monitoramento

```bash
# Status dos containers
docker-compose ps

# Uso de recursos
docker stats

# Informações detalhadas de um container
docker inspect taiglo_api_gateway
```

## 📊 Dados de Teste

O sistema vem pré-populado com:

### Categorias
- Cafés
- Restaurantes  
- Parques
- Museus
- Arte e Cultura

### Experiências (20+)
- **Vila Madalena:** Cafés e bares únicos
- **Pinheiros:** Restaurantes e experiências gastronômicas
- **Centro:** Museus e pontos culturais
- **Jardins:** Experiências premium
- **Ibirapuera:** Parques e atividades ao ar livre

### Usuários de Teste
- **Admin:** admin@taiglo.com / admin123
- **Teste:** teste@taiglo.com / senha123
- **Local Guide:** guide@taiglo.com / guide123

## 🔐 Configurações de Segurança

### Variáveis de Ambiente

Para produção, altere estas variáveis no `docker-compose.yml`:

```yaml
environment:
  - JWT_SECRET_KEY=seu_jwt_secret_muito_seguro_aqui
  - POSTGRES_PASSWORD=senha_muito_segura_aqui
  - REDIS_PASSWORD=senha_redis_segura_aqui
```

### CORS

O sistema está configurado para aceitar requisições de `localhost:5173`. Para produção, atualize as configurações de CORS nos serviços.

## 📈 Performance

### Otimizações Implementadas

- **Cache Redis** para consultas frequentes
- **Connection Pooling** no PostgreSQL
- **Índices geoespaciais** para busca por proximidade
- **Compressão** nas respostas das APIs
- **Health checks** para monitoramento

### Métricas

```bash
# Verificar performance do banco
docker-compose exec postgres psql -U taiglo_user -d taiglo_db -c "SELECT * FROM pg_stat_activity;"

# Verificar cache Redis
docker-compose exec redis redis-cli info stats
```

## 🚀 Deploy em Produção

### Preparação

1. **Alterar senhas** em todas as variáveis de ambiente
2. **Configurar HTTPS** com certificados SSL
3. **Configurar domínio** e DNS
4. **Ajustar CORS** para o domínio de produção
5. **Configurar backup** automático do banco

### Docker Compose para Produção

```yaml
# Adicionar ao docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
```

## 📞 Suporte

### Informações do Sistema

```bash
# Versões dos serviços
docker-compose exec api-gateway python --version
docker-compose exec frontend node --version

# Informações do banco
docker-compose exec postgres psql -U taiglo_user -d taiglo_db -c "SELECT version();"
```

### Coleta de Logs para Suporte

```bash
# Gerar arquivo com todos os logs
docker-compose logs > taiglo_logs.txt

# Informações do sistema
docker-compose ps > taiglo_status.txt
docker system info > docker_info.txt
```

---

## ✅ Checklist de Verificação

Após o setup, verifique se:

- [ ] Todos os containers estão rodando (`docker-compose ps`)
- [ ] Frontend acessível em http://localhost:5173
- [ ] API Gateway responde em http://localhost:3000/health
- [ ] Banco de dados tem dados de seed (`curl http://localhost:3000/api/experiences`)
- [ ] Login funciona com conta de teste
- [ ] Busca por proximidade retorna resultados
- [ ] Sistema de reviews está operacional

**🎉 Parabéns! O Taiglo MVP está rodando com sucesso!**

Para dúvidas ou problemas, consulte a seção de troubleshooting ou os logs detalhados dos serviços.

