FROM node:18-alpine
WORKDIR /app
COPY package.json ./
COPY . .
RUN npm install
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
