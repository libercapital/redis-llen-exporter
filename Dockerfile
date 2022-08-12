FROM python:3-slim

ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app/src

RUN set -eux; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    gosu \
    python3-yaml \
    python3-redis \
    python3-prometheus-client && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

RUN set -eux; \
    groupadd --system --gid=888 redisllenexporter && \
    useradd --system --gid=redisllenexporter --uid=888 \
            --home-dir=/usr/src/app \
            redisllenexporter && \
    mkdir -p /usr/src/app && \
    chown -R redisllenexporter:redisllenexporter /usr/src/app

COPY docker-entrypoint.sh /usr/local/bin

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

COPY redis-llen-exporter.py /usr/src/app/src

EXPOSE 9090/tcp

CMD ["python3.9", "redis-llen-exporter.py", "/redis-llen-exporter.yaml"]
