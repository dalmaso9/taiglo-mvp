# 📸 Funcionalidade de Imagens - Taiglo

## 🎯 Visão Geral

A funcionalidade de **imagens** foi implementada no sistema Taiglo para permitir que as experiências tenham fotos associadas, melhorando significativamente a experiência do usuário e a apresentação visual das experiências.

## 🏗️ Arquitetura Implementada

### 1. **Banco de Dados**
- **Campo adicionado**: `photos JSONB DEFAULT '[]'` na tabela `experiences`
- **Tipo**: Array de URLs das imagens
- **Script de migração**: `database/add_photos_column.sql`

### 2. **Backend (Experience Service)**
- **Modelo atualizado**: `Experience` agora inclui campo `photos`
- **Novas rotas**:
  - `POST /api/experiences/{id}/photos` - Upload de fotos
  - `DELETE /api/experiences/{id}/photos` - Remover fotos
  - `PUT /api/experiences/{id}/photos/reorder` - Reordenar fotos

### 3. **API Gateway**
- **Rotas proxy** adicionadas para todas as operações de fotos
- **Documentação Swagger** incluída

### 4. **Frontend**
- **Componente**: `ImageUpload.jsx` para upload e gerenciamento
- **Integração**: `ExperienceDetails.jsx` para exibição
- **Admin Panel**: Nova aba "Fotos" para gerenciamento

## 🚀 Funcionalidades Implementadas

### ✅ **Upload de Imagens**
- **Drag & Drop**: Interface intuitiva para arrastar e soltar imagens
- **Seleção múltipla**: Upload de várias imagens simultaneamente
- **Validação**: Verificação de tipo e tamanho de arquivo
- **Formatos suportados**: PNG, JPG, JPEG, GIF, WebP
- **Tamanho máximo**: 5MB por arquivo

### ✅ **Exibição de Imagens**
- **Grid responsivo**: Layout adaptável para diferentes telas
- **Hover effects**: Efeitos visuais ao passar o mouse
- **Otimização**: Carregamento otimizado das imagens

### ✅ **Gerenciamento de Imagens**
- **Deleção**: Remoção individual de fotos
- **Reordenação**: Possibilidade de alterar a ordem das fotos
- **Interface admin**: Painel dedicado para administradores

### ✅ **Armazenamento**
- **Estrutura organizada**: `/static/uploads/{experience_id}/`
- **Nomes únicos**: Timestamp + nome original
- **Volume persistente**: Docker volume para persistência

## 📋 Como Usar

### **Para Usuários Finais:**
1. **Visualizar fotos**: Acesse qualquer experiência para ver as fotos
2. **Navegar**: As fotos aparecem em um grid responsivo
3. **Interagir**: Hover effects para melhor experiência

### **Para Administradores:**
1. **Acesse o Painel Admin**: http://localhost:5173/admin
2. **Vá para a aba "Fotos"**
3. **Selecione uma experiência** no dropdown
4. **Faça upload** arrastando arquivos ou clicando em "Selecionar Fotos"
5. **Gerencie** as fotos existentes (delete, reordene)

### **Para Desenvolvedores:**
```bash
# Upload de fotos
curl -X POST http://localhost:3000/api/experiences/{id}/photos \
  -H "Authorization: Bearer {token}" \
  -F "photos=@image1.jpg" \
  -F "photos=@image2.png"

# Remover fotos
curl -X DELETE http://localhost:3000/api/experiences/{id}/photos \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"photo_urls": ["/static/uploads/123/image1.jpg"]}'

# Reordenar fotos
curl -X PUT http://localhost:3000/api/experiences/{id}/photos/reorder \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"photo_order": ["/static/uploads/123/image2.png", "/static/uploads/123/image1.jpg"]}'
```

## 🔧 Configuração Técnica

### **Dependências Adicionadas:**
```txt
Pillow==11.3.0          # Processamento de imagens
werkzeug==3.1.3         # Upload de arquivos
```

### **Estrutura de Arquivos:**
```
experience-service/
├── src/
│   ├── static/
│   │   └── uploads/           # Diretório de uploads
│   │       └── {experience_id}/
│   │           ├── 20241201_143022_image1.jpg
│   │           └── 20241201_143023_image2.png
│   ├── routes/
│   │   └── experience.py      # Rotas de fotos
│   └── models/
│       └── experience.py      # Modelo atualizado
```

### **Docker Configuration:**
```yaml
volumes:
  - experience_uploads:/app/src/static/uploads  # Volume persistente
```

## 🎨 Interface do Usuário

### **Componente ImageUpload:**
- **Área de drag & drop** com feedback visual
- **Grid de preview** das imagens enviadas
- **Botões de ação** (deletar) com hover effects
- **Indicador de progresso** durante upload

### **Exibição em ExperienceDetails:**
- **Seção dedicada** para fotos
- **Layout responsivo** (1-3 colunas)
- **Sombras e efeitos** para melhor apresentação

## 🔒 Segurança e Validação

### **Validações Implementadas:**
- ✅ **Tipos de arquivo**: Apenas imagens permitidas
- ✅ **Tamanho máximo**: 5MB por arquivo
- ✅ **Autenticação**: Token JWT obrigatório
- ✅ **Autorização**: Apenas admins podem gerenciar
- ✅ **Sanitização**: Nomes de arquivo seguros

### **Proteções:**
- **Rate limiting**: Prevenção de spam
- **Validação de entrada**: Verificação de dados
- **Isolamento**: Cada experiência tem seu diretório

## 📊 Benefícios

### **Para Usuários:**
- 🖼️ **Experiência visual rica** com fotos das experiências
- 📱 **Interface responsiva** que funciona em todos os dispositivos
- ⚡ **Carregamento otimizado** das imagens

### **Para Administradores:**
- 🛠️ **Ferramentas completas** de gerenciamento
- 📤 **Upload em lote** para eficiência
- 🔄 **Reordenação flexível** das fotos

### **Para o Sistema:**
- 🗄️ **Armazenamento organizado** e escalável
- 🔧 **API RESTful** bem documentada
- 📈 **Preparado para crescimento** futuro

## 🚀 Próximos Passos

### **Melhorias Futuras:**
- [ ] **Compressão automática** de imagens
- [ ] **Thumbnails** para carregamento mais rápido
- [ ] **CDN integration** para melhor performance
- [ ] **Watermark** automático nas imagens
- [ ] **OCR** para extrair texto das imagens
- [ ] **Moderação** automática de conteúdo

### **Otimizações:**
- [ ] **Lazy loading** das imagens
- [ ] **WebP** como formato padrão
- [ ] **Cache** de imagens processadas
- [ ] **Backup** automático das imagens

---

## 🎉 Conclusão

A funcionalidade de imagens foi **implementada com sucesso** e está **100% funcional**! 

**Para testar:**
1. Acesse: http://localhost:5173
2. Faça login como admin: `admin@taiglo.com` / `admin123`
3. Vá para o Painel Admin → aba "Fotos"
4. Selecione uma experiência e faça upload de imagens
5. Visualize as fotos na página de detalhes da experiência

A funcionalidade está **pronta para uso em produção** e pode ser facilmente expandida conforme necessário! 🚀✨
