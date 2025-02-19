# Use the base image from NodeJS 18 on debian to install the NREL certs
FROM node:18-bullseye AS certificates

# Install NREL root certs.
RUN curl -fsSLk -o /usr/local/share/ca-certificates/nrel_root.crt https://raw.github.nrel.gov/TADA/nrel-certs/v20180329/certs/nrel_root.pem && \
    curl -fsSLk -o /usr/local/share/ca-certificates/nrel_xca1.crt https://raw.github.nrel.gov/TADA/nrel-certs/v20180329/certs/nrel_xca1.pem && \
    update-ca-certificates

FROM node:18-alpine AS build

# Copy the installed SSL certs into this image
COPY --from=certificates /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt
COPY --from=certificates /usr/share/ca-certificates /usr/share/ca-certificates
COPY --from=certificates /usr/local/share/ca-certificates /usr/local/share/ca-certificates

ARG VITE_API_BASE_URL
ARG VITE_MAP_API_KEY
ARG VITE_MAP_ID

ENV NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt \
  VITE_API_BASE_URL=${VITE_API_BASE_URL} \
  VITE_MAP_API_KEY=${VITE_MAP_API_KEY} \
  VITE_MAP_ID=${VITE_MAP_ID}

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --silent

COPY . .

RUN yarn build

# TODO use split NGINX
FROM nginx:alpine

RUN apk add --no-cache ca-certificates

COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
