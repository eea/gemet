FROM python:2.7-slim
RUN runDeps="libmysqlclient-dev gcc libldap2-dev libxml2-dev libxslt1-dev" \
 && apt-get update -y \
 && apt-get install -y --no-install-recommends $runDeps \
 && rm -vrf /var/lib/apt/lists/*
COPY . /gemet
RUN chmod 755 /gemet/docker-entrypoint.sh
WORKDIR /gemet
RUN pip install -r requirements.txt
ENTRYPOINT ["./docker-entrypoint.sh"]