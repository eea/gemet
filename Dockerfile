FROM python:2.7-slim

LABEL maintainer="European Environment Agency (EEA): IDM2 S-Team"

ENV PROJ_DIR=/var/local/gemet

RUN runDeps="gcc default-libmysqlclient-dev default-mysql-client libldap2-dev libsasl2-dev libxml2-dev libxslt1-dev netcat-traditional" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*

RUN mkdir -p $PROJ_DIR
COPY . $PROJ_DIR
WORKDIR $PROJ_DIR
RUN mv gemet/local_settings.py.docker gemet/local_settings.py

RUN sed '/st_mysql_options options;/a unsigned int reconnect;' /usr/include/mysql/mysql.h -i.bkp

RUN pip install -r requirements-docker.txt

ENTRYPOINT ["./docker-entrypoint.sh"]
