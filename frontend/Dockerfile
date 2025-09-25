# Estágio 1: Construção (Build)
FROM node:20-alpine AS build
WORKDIR /app

# Copia os manifestos de pacotes
COPY package.json pnpm-lock.yaml ./

# Instala o pnpm e as dependências do projeto
RUN npm install -g pnpm
RUN pnpm install

# Copia o restante do código-fonte
COPY . .

# Gera a versão final e otimizada da aplicação na pasta /dist
RUN pnpm run build

# Estágio 2: Produção (Servidor)
FROM nginx:stable-alpine
# Copia os arquivos da pasta /dist do estágio anterior para a pasta do Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Expõe a porta 80, que é a porta padrão do Nginx
EXPOSE 80

# O Nginx inicia automaticamente, então não precisamos do comando CMD
    
