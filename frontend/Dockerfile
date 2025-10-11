# --- deps & build
FROM node:20-alpine AS build
WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ /app/

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# --- runtime
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist/ /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
