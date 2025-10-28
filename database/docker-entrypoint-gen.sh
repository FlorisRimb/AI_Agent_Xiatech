#!/bin/bash
set -euo pipefail

export_vars='${DATABASE_NAME} ${DATABASE_USER} ${DATABASE_PASSWORD}'

for template in /docker-entrypoint-initdb.d/*.js.template; do
  if [ -f "$template" ]; then
    output="${template%.template}"
    echo "Generating $output from $template"
    envsubst "$export_vars" < "$template" > "$output"
  fi
done

exec /usr/local/bin/docker-entrypoint.sh "$@"