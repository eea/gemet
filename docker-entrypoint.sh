#!/bin/bash

set -e

COMMANDS="qcluster"

if [ -z "$MYSQL_ADDR" ]; then
  MYSQL_ADDR="mysql"
fi

while ! nc -z $MYSQL_ADDR 3306; do
  echo "Waiting for MySQL server at '$MYSQL_ADDR' to accept connections on port 3306..."
  sleep 1s
done

if [ -z "$1" ]; then
  python manage.py migrate &&
  python manage.py collectstatic --noinput &&
  python manage.py fetch_templates_plone &&
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
