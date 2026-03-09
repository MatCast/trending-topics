FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.output ./.output

ENV PORT=8080
EXPOSE 8080

CMD ["node", ".output/server/index.mjs"]
