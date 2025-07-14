import time
import json
import logging
import pika
from pika.exceptions import AMQPConnectionError, ChannelClosed
from parser_service.app.config.settings import get_settings

logger = logging.getLogger(__name__)


class RabbitMQPublisher:
    def __init__(self, settings=None):
        self.settings = settings or get_settings()
        creds = pika.PlainCredentials(
            self.settings.rabbitmq_user,
            self.settings.rabbitmq_pass
        )
        params = pika.ConnectionParameters(
            host=self.settings.rabbitmq_host,
            port=self.settings.rabbitmq_port,
            credentials=creds
        )
        try:
            self.conn = pika.BlockingConnection(params)
            self.channel = self.conn.channel()
            self.channel.exchange_declare(
                exchange=self.settings.exchange,
                exchange_type="direct",
                durable=True
            )
        except AMQPConnectionError as e:
            logger.error("Failed to connect to RabbitMQ", exc_info=True)
            raise RuntimeError("Failed to connect to RabbitMQ") from e

    def publish_summary_job(self, request_id: str, filename: str, text: str):
        message = json.dumps({
            "request_id": request_id,
            "filename": filename,
            "text": text
        })

        retries = 0
        while retries <= self.settings.max_retries:
            try:
                self.channel.basic_publish(
                    exchange=self.settings.exchange,
                    routing_key=self.settings.routing_key,
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                logger.info(f"Published summary job for file '{filename}' (request_id={request_id})")
                return
            except (AMQPConnectionError, ChannelClosed) as e:
                retries += 1
                delay = self.settings.retry_delay ** (retries - 1)
                if retries > self.settings.max_retries:
                    logger.error(f"Failed to publish after {retries} retries", exc_info=True)
                    raise RuntimeError(
                        f"Failed to publish after {retries} attempts: {e}"
                    ) from e

                logger.warning(
                    f"Retry {retries}/{self.settings.max_retries} in {delay}s "
                    f"due to transient error: {e}"
                )
                time.sleep(delay)
            except Exception as e:
                logger.error("Unexpected error during RabbitMQ publish", exc_info=True)
                raise RuntimeError(
                    f"Unexpected error while publishing to RabbitMQ: {e}"
                ) from e

    def close(self):
        if hasattr(self, "conn") and self.conn and self.conn.is_open:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
