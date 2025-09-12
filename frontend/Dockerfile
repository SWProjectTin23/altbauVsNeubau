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

RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001 -G appgroup

RUN rm /etc/nginx/conf.d/default.conf

COPY --from=build /app/nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

RUN chown -R appuser:appgroup /var/cache/nginx /var/run /usr/share/nginx/html
USER appuser


# Start Nginx in the foreground.
CMD ["nginx", "-g", "daemon off;"]