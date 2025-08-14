#!/bin/sh
set -eu

DB="/app/data/kuma.db"
USER="${KUMA_ADMIN_USERNAME:-admin}"
PASS="${KUMA_ADMIN_PASSWORD:-}"
FORCE="${KUMA_FORCE_SET_PASSWORD:-true}"

# Uptime-Kuma starten
node server/server.js &
PID=$!

echo "[kuma] waiting for DB file..."
i=0
while [ $i -lt 90 ]; do
  if [ -f "$DB" ]; then
    break
  fi
  i=$((i+1))
  sleep 1
done

if [ -n "$PASS" ] && [ -f "$DB" ]; then
  # Bcrypt-Hash robust erzeugen (kein -e; keine Quote-Hölle)
  HASH="$(PASS="$PASS" node -p 'require("bcryptjs").hashSync(process.env.PASS, 10)')"

  echo "[kuma] waiting for 'user' table..."
  i=0
  while [ $i -lt 60 ]; do
    if sqlite3 "$DB" ".schema user" >/dev/null 2>&1; then
      break
    fi
    i=$((i+1))
    sleep 1
  done

  # Existiert der User?
  EXISTS="$(sqlite3 "$DB" "SELECT COUNT(1) FROM user WHERE username='${USER}'" 2>/dev/null || echo 0)"

  if [ "$EXISTS" = "1" ]; then
    CURR="$(sqlite3 "$DB" "SELECT password FROM user WHERE username='${USER}'" || echo "")"
    if [ "$FORCE" = "true" ] || [ "$CURR" != "$HASH" ]; then
      echo "[kuma] updating password for '${USER}'"
      n=0
      while [ $n -lt 10 ]; do
        if sqlite3 "$DB" "UPDATE user SET password='${HASH}' WHERE username='${USER}'"; then
          sqlite3 "$DB" "DELETE FROM session;" || true
          break
        fi
        n=$((n+1))
        sleep 1
      done
    else
      echo "[kuma] password already up-to-date"
    fi
  else
    echo "[kuma] creating admin user '${USER}'"
    n=0
    while [ $n -lt 10 ]; do
      if sqlite3 "$DB" "INSERT INTO user (username, password, isActive, role) VALUES ('${USER}', '${HASH}', 1, 'admin');"; then
        break
      fi
      n=$((n+1))
      sleep 1
    done
  fi

  # Geheimnis aus Env löschen (Hardening)
  unset KUMA_ADMIN_PASSWORD || true
fi

wait $PID
