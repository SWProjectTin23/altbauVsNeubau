# Node.js Basis-Image
FROM node:20-alpine

# load working directory
WORKDIR /app

# Install curl for health checks
RUN apk add --no-cache curl

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