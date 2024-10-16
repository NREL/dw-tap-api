FROM node:18-alpine

WORKDIR /app

EXPOSE 3000

COPY package.json package-lock.json ./

RUN yarn install --silent

COPY . ./

CMD ["yarn", "start"]