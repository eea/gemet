FROM python:2.7-slim
RUN runDeps="libmysqlclient-dev gcc libldap2-dev libxml2-dev libxslt1-dev nginx" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*
COPY gemet_nginx.conf /etc/nginx/sites-enabled/default
COPY . /gemet
RUN chmod 755 /gemet/docker-entrypoint.sh
WORKDIR /gemet
RUN pip install -r requirements-docker.txt
ENTRYPOINT ["./docker-entrypoint.sh"]