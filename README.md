# Redis List Length Exporter for Prometheus

Gets the length of the specified keys and make available for Prometheus collections.

A configuration file must be mounted in `/redis-llen-exporter.yaml` with a list of Redis intances and the keys that should be metered for that instance.

For example:

```yaml

instances:
  sample-instance:
    host: redis
    port: 6379
    db: 0
    ssl: false
    username:
    password:

    keys:
      - queue1
      - queue2
      - stack
      - "something with spaces"

```

Source code: https://github.com/libercapital/redis-llen-exporter
Docker images: https://hub.docker.com/repository/docker/libercapital/redis-llen-exporter
