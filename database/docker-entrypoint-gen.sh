#!/bin/bash
set -euo pipefail

if [ -f /docker-entrypoint-initdb.d/init-mongo.js.template ]; then
  envsubst < /docker-entrypoint-initdb.d/init-mongo.js.template > /docker-entrypoint-initdb.d/init-mongo.js
fi

exec /usr/local/bin/docker-entrypoint.sh "$@"