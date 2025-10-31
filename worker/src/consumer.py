from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import pika

from .settings import settings


logger = logging.getLogger(__name__)


@dataclass
class MessageContext:
    delivery_tag: int
    body: bytes


def create_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(settings.rabbitmq_user, settings.rabbitmq_pass)
    params = pika.ConnectionParameters(host=settings.rabbitmq_host, port=settings.rabbitmq_port, credentials=credentials)
    return pika.BlockingConnection(params)


def consume(callback) -> None:
    connection = create_connection()
    channel = connection.channel()
    channel.queue_declare(queue=settings.rabbitmq_queue, durable=True)

    def _on_message(ch, method, properties, body):
        logger.info("Received message: %s", body)
        try:
            callback(MessageContext(delivery_tag=method.delivery_tag, body=body))
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Processing failed; NACKing message: %s", exc)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=settings.rabbitmq_queue, on_message_callback=_on_message)
    logger.info("Started consuming queue=%s", settings.rabbitmq_queue)
    try:
        channel.start_consuming()
    finally:
        channel.close()
        connection.close()


