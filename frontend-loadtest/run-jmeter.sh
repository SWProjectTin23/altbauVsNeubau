#!/usr/bin/env bash
set -euo pipefail

# --- Load optional .env ---
set -a; [ -f .env ] && . ./.env; set +a

# --- Defaults ---
FRONTCONT="${FRONTCONT:-altbau_vs_neubau_frontend}"   # your frontend container name
USERS="${USERS:-15}"
RAMP="${RAMP:-15}"

RESULTS_DIR="${RESULTS_DIR:-results}"
REPORT_DIR="${RESULTS_DIR}/report"        # fixed directory (we'll empty its contents only)
JTL_FILE="${RESULTS_DIR}/results.jtl"
LOG_FILE="${RESULTS_DIR}/jmeter.log"

mkdir -p "${REPORT_DIR}"

# --- Clean previous results WITHOUT deleting the folder ---
# (use a tiny root container so we don't hit permission issues)
docker run --rm -v "$PWD/${RESULTS_DIR}:/results" alpine sh -c '
  mkdir -p /results/report
  # remove everything inside report (files & subfolders), keep the dir
  find /results/report -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
  # remove old jtl/log
  rm -f /results/results.jtl /results/jmeter.log 2>/dev/null || true
'

# --- Figure out networking & targets ---
NET_ARGS=(); EXTRA_ARGS=()
TARGET_URL_DEFAULT="http://altbau_vs_neubau_frontend"
API_BASE_DEFAULT="http://altbau_vs_neubau_api:5000/api"

if docker inspect "$FRONTCONT" >/dev/null 2>&1; then
  COMPOSE_NETWORK="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{printf "%s" $k}}{{end}}' "$FRONTCONT")"
  if docker network inspect "${COMPOSE_NETWORK}" >/dev/null 2>&1; then
    echo "→ Using Docker network: ${COMPOSE_NETWORK}"
    NET_ARGS+=(--network "${COMPOSE_NETWORK}")
    TARGET_URL="${TARGET_URL:-$TARGET_URL_DEFAULT}"
    API_BASE="${API_BASE:-$API_BASE_DEFAULT}"
  fi
fi

# Fallback to host ports if no network was set
if [[ ${#NET_ARGS[@]} -eq 0 ]]; then
  echo "⚠️  No compose network found — using host ports."
  TARGET_URL="${TARGET_URL:-http://host.docker.internal:3000}"
  API_BASE="${API_BASE:-http://host.docker.internal:5001/api}"
  [[ "$(uname -s)" == "Linux" ]] && EXTRA_ARGS+=(--add-host=host.docker.internal:host-gateway)
fi

echo "USERS=${USERS}  RAMP=${RAMP}"
echo "TARGET_URL=${TARGET_URL}"
echo "API_BASE=${API_BASE}"

# --- Run JMeter ---
docker run --rm \
  "${NET_ARGS[@]}" "${EXTRA_ARGS[@]}" \
  -v "$(pwd)/jmeter:/test" \
  -v "$(pwd)/${RESULTS_DIR}:/results" \
  justb4/jmeter:latest \
  -n -t /test/plan.jmx \
  -f \
  -Jtarget_url="${TARGET_URL}" \
  -Japi_base="${API_BASE}" \
  -Jusers="${USERS}" -Jramp="${RAMP}" \
  -l /results/results.jtl \
  -e -o /results/report \
  -j /results/jmeter.log \
  -Dlog_level.jmeter=INFO

# --- Make files owned by you (no sudo needed next time) ---
docker run --rm -v "$PWD/${RESULTS_DIR}:/results" alpine sh -c "chown -R $(id -u):$(id -g) /results" || true


