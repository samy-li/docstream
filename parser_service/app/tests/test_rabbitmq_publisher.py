import os
import json
import pytest
import pika
import uuid
from parser_service.app.messaging.rabbitmq_publisher import RabbitMQPublisher
from parser_service.app.config.settings import Settings

TEST_QUEUE_NAME = "test_summary_queue"

@pytest.fixture(scope="module")
def rabbitmq_channel():
    # connect and create test queue
    host = os.getenv("RABBITMQ_HOST", "localhost")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))
    channel = connection.channel()
    channel.queue_declare(queue=TEST_QUEUE_NAME, durable=True)
    yield channel
    # Teardown
    channel.queue_delete(queue=TEST_QUEUE_NAME)
    connection.close()

@pytest.fixture
def test_publisher():
    # Override settings to use test queue and direct values
    test_settings = Settings(
        rabbitmq_host="localhost",
        rabbitmq_port=5672,
        rabbitmq_user="guest",
        rabbitmq_pass="guest",
        exchange="resumate_exchange",
        queue=TEST_QUEUE_NAME,
        routing_key="test_key",
        dlx="",
        dlq="",
        max_retries=2,
        retry_delay=1
    )
    return RabbitMQPublisher(settings=test_settings)

def test_publish_summary_job_sends_message(rabbitmq_channel, test_publisher):
    request_id = str(uuid.uuid4())
    test_filename = "test_doc.pdf"
    test_text = "Test extracted text."

    test_publisher.publish_summary_job(request_id, test_filename, test_text)

    method_frame, header_frame, body = rabbitmq_channel.basic_get(TEST_QUEUE_NAME, auto_ack=True)

    assert method_frame is not None, "No message received from queue"
    payload = json.loads(body)
    assert payload["request_id"] == request_id
    assert payload["filename"] == test_filename
    assert payload["text"] == test_text
