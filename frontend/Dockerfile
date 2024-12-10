FROM node:18-slim

WORKDIR /app

RUN apt-get update && \
  apt-get install -y build-essential

ENV YARN_IGNORE_OPTIONAL false

COPY package.json yarn.lock ./

RUN yarn --frozen-lockfile

# Debug: Check if the module is installed
RUN ls -R node_modules/@rollup || echo "Module not found"

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
