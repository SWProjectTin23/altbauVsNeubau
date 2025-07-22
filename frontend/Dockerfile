# Node.js Basis-Image
FROM node:18-alpine

# load working directory
WORKDIR /app

# copy package.json and package-lock.json
COPY package*.json ./

# install dependencies
RUN npm install

# copy application code
COPY . .

# release port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]