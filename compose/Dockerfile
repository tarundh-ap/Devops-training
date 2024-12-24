FROM node:lts-alpine

WORKDIR /app

COPY . .

RUN npm install --production

CMD [ "node", "server.js" ]
