FROM python:2.7-slim

ENV PROJ_DIR=/var/local/gemet

RUN runDeps="libmysqlclient-dev gcc libldap2-dev libxml2-dev libxslt1-dev nginx" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

COPY gemet_nginx.conf /etc/nginx/sites-enabled/default

COPY . $PROJ_DIR

RUN chmod 755 $PROJ_DIR/docker-entrypoint.sh

WORKDIR $PROJ_DIR

RUN pip install -r requirements-docker.txt

ENTRYPOINT ["./docker-entrypoint.sh"]