# ---------- 1️⃣ Build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependency files
COPY package*.json ./

# Install dependencies
RUN npm install

# ✅ Copy .env before build so Vite picks it up
COPY .env ./

# Copy source and build
COPY . .
RUN npm run build


# ---------- 2️⃣ Serve stage ----------
FROM nginx:1.25-alpine
WORKDIR /usr/share/nginx/html

# Copy built assets from builder
COPY --from=builder /app/dist ./

# Copy custom nginx config (optional)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
