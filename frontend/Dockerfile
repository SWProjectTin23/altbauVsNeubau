# Use a node image to build the frontend application
FROM node:20-alpine AS build

# Set the working directory inside the container
WORKDIR /app

# copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the entire application source code
COPY . .

# Build the application for production.
# NOTE: This is where the VITE_API_URL is compiled into the static assets.
RUN npm run build

# Use a very slim Nginx image to serve the static files.
FROM nginx:alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration that you created
COPY --from=build /app/nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copy the built static files into the Nginx web server folder.
# IMPORTANT: Changed path from /app/dist to /app/build!
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

# Start Nginx in the foreground.
CMD ["nginx", "-g", "daemon off;"]