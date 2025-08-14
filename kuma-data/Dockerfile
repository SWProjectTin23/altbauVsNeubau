# Nutze das Alpine-Tag, damit apk verfügbar ist
FROM louislam/uptime-kuma:1-alpine

# sqlite CLI für Passwort-Update
RUN apk add --no-cache sqlite

# Entrypoint, der das Admin-Passwort setzt
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
