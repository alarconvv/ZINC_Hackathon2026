# Builds the Expo web export and serves it with nginx for local Docker testing.
# Build context: mobileApp/ (see docker-compose.yml at the repository root).
FROM node:24 AS build
WORKDIR /work/mobile
COPY . /work
# Windows checkouts can contain CRLF endings; the legal pages split paragraphs on blank lines.
RUN sed -i 's/\r$//' /work/privacy.md /work/terms.md
RUN npm ci --no-audit --no-fund
# Public API origin compiled into the bundle; never a secret.
ARG EXPO_PUBLIC_API_URL=http://127.0.0.1:8000
ENV EXPO_PUBLIC_API_URL=$EXPO_PUBLIC_API_URL CI=1 EXPO_NO_TELEMETRY=1
RUN npm run build:web

FROM nginx:alpine
COPY mobile/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /work/mobile/dist /usr/share/nginx/html
