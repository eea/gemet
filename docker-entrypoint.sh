#!/bin/bash

set -e

cd /gemet

python manage.py migrate &&
python manage.py collectstatic --noinput &&
/usr/sbin/nginx &&
exec gunicorn gemet.wsgi:application \
	--name gemet \
	--bind 0.0.0.0:8888 \
	--workers 3 \
	--access-logfile - \
	--error-logfile -

