#!/usr/bin/env python

import os
import sys
import time
import yaml

from prometheus_client import start_http_server, Gauge
from redis import exceptions as redis_exceptions
from redis import Redis


# Anatomy of a prometheus metric
# Class -> metric type: Summary, Gauge, Histogram, etc
#
# Declaration:
#
# Class('metric_name', 'Human Readable Description', ['my_label1'])
redis_list_length = Gauge(
    "redis_list_length", "Redis List Length", ["key", "db", "instance"]
)


def update_stats(instances, connections):
    for name, instance in instances.items():
        # TODO: replace by logging
        print("Updating stats for instance:", name)

        for key in instance["keys"]:
            connection = connections[name]
            get_key_llen(name, instance["db"], key, connection)


def get_key_llen(instance_name, db, key, connection):
    try:
        len = connection.llen(key)
        redis_list_length.labels(
            instance=instance_name,
            db=db,
            key=key,
        ).set(len)
    except redis_exceptions.RedisError as excpt:
        # TODO: replace by logging
        print(excpt)
        raise


def connect(connection_options):
    connection = Redis(**connection_options)
    try:
        connection.ping()
    except redis_exceptions.RedisError as excpt:
        # TODO: replace by logging
        print(excpt)
        raise
    return connection


def connect_to_all_instances(instances):
    connections = {}
    for name, instance in instances.items():
        connect_options = {
            "host": instance["host"],
            "db": instance["db"],
        }

        options = ["port", "ssl", "username", "password"]
        for option in options:
            if option in instance:
                connect_options[option] = instance[option]

        connections[name] = connect(connect_options)

    return connections


def validate_config(instances):
    for name, instance in instances.items():
        if "keys" not in instance:
            raise Exception(
                "Missing keys for length monitoring in instance '%s'" % name
            )

        if "host" not in instance:
            raise Exception("Missing host in instance '%s'" % name)

        if "db" not in instance:
            raise Exception("Missing db in instance '%s'" % name)


def get_instances_from_config():
    config_file_path = sys.argv[1]
    with open(config_file_path) as config_file:
        data = yaml.safe_load(config_file)

    validate_config(data["instances"])

    return data["instances"]


def main():
    instances = get_instances_from_config()
    connections = connect_to_all_instances(instances)

    # Start up the server to expose the metrics.
    bind_addr = os.getenv("REDIS_LLEN_EXPORTER_BIND_ADDR", "127.0.0.1")
    start_http_server(9090, bind_addr)

    while True:
        time.sleep(30)
        try:
            update_stats(instances, connections)

        # Catch some exceptions and return True to restart the service
        # For example: temporary Redis Failure
        except redis_exceptions.RedisError:
            return True


if __name__ == "__main__":
    restart = main()
    while restart:
        restart = main()
