# --- Base Stage ---
FROM node:20-alpine AS base
WORKDIR /app
COPY package.json package-lock.json ./

# --- Dependencies Stage ---
FROM base AS dependencies
RUN npm ci

# --- Development Stage ---
FROM dependencies AS development
COPY . .
ENV PORT=3000
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# --- Builder Stage ---
FROM dependencies AS builder
COPY . .
RUN npm run build

# --- Production Stage ---
FROM base AS production
WORKDIR /app
COPY --from=builder /app/.output ./.output
ENV PORT=8080
EXPOSE 8080
CMD ["node", ".output/server/index.mjs"]
