# --- Deps & build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./

COPY frontend/ /app/

RUN addgroup --system pwuser \
 && adduser  --system --ingroup pwuser --disabled-password --home /home/pwuser pwuser
RUN chown -R pwuser:pwuser /app
USER pwuser

FROM node:20-alpine AS build

# Network-resilient npm settings
# - fewer network calls (no audit/fund)
# - more retries/timeouts
# - cache dir
RUN npm set progress=false \
 && npm config set fetch-retries 5 \
 && npm config set fetch-retry-maxtimeout 120000 \
 && npm config set fetch-timeout 120000 \
 && npm config set registry "https://registry.npmjs.org/" \
 && npm ci --no-audit --no-fund

ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# Runtime
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist/ /usr/share/nginx/html/
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Smaller logs
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
 && ln -sf /dev/stderr /var/log/nginx/error.log
 
EXPOSE 80

CMD nginx -g 'daemon off;'
