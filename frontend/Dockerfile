FROM node:18-alpine AS build

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install --silent

COPY . .

RUN yarn build

FROM nginx:alpine

RUN apk add --no-cache ca-certificates

ARG API_GATEWAY_HOST=placeholder
ENV API_GATEWAY_HOST=${API_GATEWAY_HOST}
ENV API_GATEWAY_URL=https://${API_GATEWAY_HOST}/prod/

COPY --from=build /app/dist /usr/share/nginx/html

COPY default.conf.template /etc/nginx/templates/default.conf.template

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
