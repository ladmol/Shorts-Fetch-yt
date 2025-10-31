from __future__ import annotations

import json

import pika

from .settings import settings


def _channel():
    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_pass)
    params = pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(params)
    ch = connection.channel()
    return connection, ch


def publish(queue: str, payload: dict) -> None:
    connection, ch = _channel()
    try:
        ch.queue_declare(queue=queue, durable=True)
        body = json.dumps(payload).encode("utf-8")
        ch.basic_publish(exchange="", routing_key=queue, body=body, properties=pika.BasicProperties(delivery_mode=2))
    finally:
        ch.close()
        connection.close()


