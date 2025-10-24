# Estágio 1: Construir a aplicação React
FROM node:18-alpine AS builder

WORKDIR /app

# --- CORREÇÃO APLICADA AQUI ---
# Instala o pnpm, que é o gerenciador de pacotes correto para este projeto.
RUN npm install -g pnpm

# Copia os ficheiros de definição de dependências
COPY package.json pnpm-lock.yaml ./

# Instala as dependências usando pnpm
RUN pnpm install

# Copia o resto do código da aplicação
COPY . .

# Constrói a aplicação para produção
RUN pnpm build

# Estágio 2: Servir a aplicação com Nginx
FROM nginx:stable-alpine

# Copia a build do estágio anterior para o diretório do Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Expõe a porta 80
EXPOSE 80

# Comando para iniciar o Nginx
CMD ["nginx", "-g", "daemon off;"]