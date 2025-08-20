# 1) Ordner & Timestamp
mkdir -p kuma_data/backups
TS=$(date +%F_%H%M%S)

# 2) Dateipaket aus dem Container streamen und lokal entpacken
docker exec uptime-kuma sh -lc 'cd /app/data && tar cf - kuma.db kuma.db-wal kuma.db-shm 2>/dev/null' \
| tar xf - -C kuma_data/backups

# 3) Sauber umbenennen (mit Timestamp)
[ -f kuma_data/backups/kuma.db ]     && mv kuma_data/backups/kuma.db     "kuma_data/backups/run-$TS.db"
[ -f kuma_data/backups/kuma.db-wal ] && mv kuma_data/backups/kuma.db-wal "kuma_data/backups/run-$TS.db-wal"
[ -f kuma_data/backups/kuma.db-shm ] && mv kuma_data/backups/kuma.db-shm "kuma_data/backups/run-$TS.db-shm"

# 4) Ergebnis kontrollieren
ls -lah kuma_data/backups | grep "run-$TS"
