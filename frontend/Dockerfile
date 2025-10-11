# --- deps & build
FROM node:20-alpine AS build
WORKDIR /app
# cache deps
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
# now copy source and build
COPY frontend/ /app/
RUN npm run build

# --- nginx runtime to serve static build
FROM nginx:1.27-alpine AS runtime
# copy built assets
COPY --from=build /app/dist/ /usr/share/nginx/html/
# optional: custom nginx.conf if you need SPA fallback
# COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
