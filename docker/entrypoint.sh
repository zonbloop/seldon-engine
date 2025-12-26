#!/bin/sh
set -eu

echo "[seldon-engine] starting container..."

mkdir -p /app/storage/logs

# Allow runtime override of cron schedule
if [ -n "${CRON_SCHEDULE:-}" ]; then
  echo "[seldon-engine] applying CRON_SCHEDULE=${CRON_SCHEDULE}"
  sed -i "s|^[0-9\*\/,-]\+[[:space:]]\+[0-9\*\/,-]\+[[:space:]]\+[0-9\*\/,-]\+[[:space:]]\+[0-9\*\/,-]\+[[:space:]]\+[0-9\*\/,-]\+|${CRON_SCHEDULE}|g" \
    /etc/cron.d/seldon-engine
  crontab /etc/cron.d/seldon-engine
fi

echo "[seldon-engine] active cron jobs:"
crontab -l || true

echo "[seldon-engine] cron running..."
exec cron -f