# Build
FROM node:24-alpine AS build

WORKDIR /app

RUN addgroup -g 1001 -S nodegroup && adduser -S nodeuser -u 1001 -G nodegroup

COPY --chown=nodeuser:nodegroup /frontend/package*.json ./
RUN npm ci

COPY --chown=nodeuser:nodegroup ./frontend .
COPY --chown=nodeuser:nodegroup ../docs/docs_full.md /app/public/docs/docs_full.md
COPY --chown=nodeuser:nodegroup ../docs/images /app/public/docs/images

USER nodeuser
RUN npm run build

# Runtime: Tag seems pretty
FROM nginx:1.29.1-alpine

RUN rm /etc/nginx/conf.d/default.conf

COPY --from=build /app/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

# Start Nginx in the foreground. => Ran in root due to it being port<1028 => https://unix.stackexchange.com/questions/134301/why-does-nginx-starts-process-as-root
CMD ["nginx", "-g", "daemon off;"]