#!/bin/bash

set -e

COMMANDS="qcluster"

if [ -z "$POSTGRES_ADDR" ]; then
  POSTGRES_ADDR="db"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgresql server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if [ -z "$1" ]; then
  python manage.py migrate &&
  python manage.py collectstatic --noinput &&
  exec gunicorn gemet.wsgi:application \
         --name gemet \
         --bind 0.0.0.0:8888 \
         --workers 3 \
         --access-logfile - \
         --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py "$@"
fi
