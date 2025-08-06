import json
import logging
import pika

from worker_service.app.config.settings import get_settings
from worker_service.app.interfaces.procesor_client_interface import (
    ProcessorClientInterface, ProcessorRequest)

logger = logging.getLogger(__name__)
settings = get_settings()


class Consumer:
    """
    RabbitMQ consumer that processes jobs using a processor client.
    Implements DLQ support and retry with header-based attempt tracking.
    """

    def __init__(self, client: ProcessorClientInterface):
        self.client = client

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user, settings.rabbitmq_pass
        )
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host="/",
            credentials=credentials
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        self._setup_exchanges_and_queues()

    def _setup_exchanges_and_queues(self):
        """
        Declare exchanges and queues, including DLX and retry setup.
        """
        self.channel.exchange_declare(
            exchange=settings.dlx,
            exchange_type="direct",
            durable=True
        )
        self.channel.queue_declare(queue=settings.dlq, durable=True)
        self.channel.queue_bind(
            queue=settings.dlq,
            exchange=settings.dlx,
            routing_key=settings.routing_key
        )

        self.channel.exchange_declare(
            exchange=settings.exchange,
            exchange_type="direct",
            durable=True
        )
        self.channel.queue_declare(
            queue=settings.queue,
            durable=True,
            arguments={
                "x-dead-letter-exchange": settings.dlx,
                "x-dead-letter-routing-key": settings.routing_key
            }
        )
        self.channel.queue_bind(
            queue=settings.queue,
            exchange=settings.exchange,
            routing_key=settings.routing_key
        )

    def _handle_message(self, ch, method, props, body):
        """
        Callback to handle a single message from RabbitMQ.
        """
        request_id = "unknown"
        try:
            payload = json.loads(body)
            request_id = payload.get("request_id")
            text = payload.get("text")
            retries = (props.headers or {}).get("x-retries", 0)

            logger.info("Received job %s (attempt %d)", request_id, retries + 1)

            request = ProcessorRequest(job_id=request_id, text=text)
            success = self.client.process(request)

            if success:
                logger.info("Successfully processed job %s", request_id)
                ch.basic_ack(method.delivery_tag)
            else:
                raise Exception("Processor returned failure")

        except Exception as e:
            logger.exception("Error processing job %s: %s", request_id, str(e))

            if retries >= settings.max_retries:
                logger.error("Max retries reached for job %s, sending to DLQ", request_id)
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
            else:
                logger.warning("Retrying job %s (retry %d)", request_id, retries + 1)
                headers = props.headers or {}
                headers["x-retries"] = retries + 1
                ch.basic_reject(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """
        Start consuming messages from the queue.
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=settings.queue,
            on_message_callback=self._handle_message
        )
        logger.info(" [*] Waiting for summary jobs…")
        print("RabbitMQ is running...")
        self.channel.start_consuming()

    def close(self):
        """
        Close the RabbitMQ connection.
        """
        self.connection.close()
