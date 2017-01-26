#!/bin/bash

set -e

cd /gemet
python manage.py migrate &&
python manage.py collectstatic --noinput &&
/usr/sbin/nginx &&
exec gunicorn gemet.wsgi:application --bind 0.0.0.0:8888 --workers 3

