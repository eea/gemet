#!/bin/bash

set -e


if [ -z "$MYSQL_ADDR" ]; then
  MYSQL_ADDR="mysql"
fi

while ! nc -z $MYSQL_ADDR 3306; do
  echo "Waiting for MySQL server at '$MYSQL_ADDR' to accept connections on port 3306..."
  sleep 1s
done

if ! mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "use $DATABASES_NAME;"; then
  echo "CREATE DATABASE $DATABASES_NAME"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $DATABASES_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '$DATABASES_USER'@'%' IDENTIFIED BY '$DATABASES_PASSWORD';"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DATABASES_NAME.* TO '$DATABASES_USER'@'%';"
fi

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

