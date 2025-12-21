FROM node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE 5173

ENV NODE_ENV=production
ENV VITE_HOST=0.0.0.0

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
