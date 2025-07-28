# Node.js Basis-Image
FROM node:18-alpine

# load working directory
WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

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