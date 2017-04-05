FROM python:2.7-slim

ENV PROJ_DIR=/var/local/gemet

RUN runDeps="gcc libmysqlclient-dev libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev nginx" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

COPY gemet_nginx.conf /etc/nginx/sites-enabled/default

RUN mkdir -p $PROJ_DIR
COPY . $PROJ_DIR
WORKDIR $PROJ_DIR


RUN pip install -r requirements-docker.txt

ENTRYPOINT ["./docker-entrypoint.sh"]