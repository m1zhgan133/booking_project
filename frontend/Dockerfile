FROM node:18-alpine

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install --silent && \
    npm install react-router-dom --save && \
    npm cache clean --force

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]