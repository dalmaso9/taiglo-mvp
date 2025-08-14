FROM node:20-alpine

WORKDIR /app

# Copiar package files
COPY package.json pnpm-lock.yaml ./

# Instalar pnpm e dependências
RUN npm install -g pnpm
RUN pnpm install

# Copiar código da aplicação
COPY . .

# Expor a porta
EXPOSE 5173

# Comando para iniciar em modo desenvolvimento
CMD ["pnpm", "run", "dev", "--host"]

