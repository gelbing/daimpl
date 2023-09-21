import logging
import socket
import time
from typing import List, Protocol, Set

from confluent_kafka import Consumer, KafkaException, Producer


class MessageHandler(Protocol):
    def handle_message(self, msg):
        pass


def get_existing_topics(bootstrap_servers: str) -> Set[str]:
    """Fetch all existing topics."""
    conf = {"bootstrap.servers": bootstrap_servers}
    p = Producer(conf)
    metadata = p.list_topics(timeout=5)
    return set(metadata.topics.keys())


def wait_for_kafka(bootstrap_servers: str, max_retries=10, delay=5) -> bool:
    """Wait for Kafka to be ready."""
    host, port = bootstrap_servers.split(":")
    retries = 0

    while retries < max_retries:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect((host, int(port)))
            logging.info("Kafka is ready!")
            s.close()
            return True
        except socket.error:
            logging.info(f"Kafka is not ready yet. Retrying in {delay} seconds.")
            retries += 1
            time.sleep(delay)

    logging.error("Kafka is not ready after waiting for a while.")
    raise Exception("Kafka is not ready after waiting for a while.")


def consume_kafka_messages(
    bootstrap_servers: str, client_topics: List[str], handler: MessageHandler
):
    wait_for_kafka(bootstrap_servers)

    c = Consumer(
        {
            "bootstrap.servers": bootstrap_servers,
            "group.id": "server-consumer-group",
            "auto.offset.reset": "earliest",
        }
    )

    subscribed_topics = set()

    while True:
        existing_topics = get_existing_topics(bootstrap_servers)
        new_topics = [
            topic
            for topic in client_topics
            if topic in existing_topics and topic not in subscribed_topics
        ]
        if new_topics:
            all_topics_to_subscribe = list(subscribed_topics) + new_topics
            c.subscribe(all_topics_to_subscribe)
            subscribed_topics.update(new_topics)
            logging.info(f"Subscribed to new topics: {new_topics}")

        try:
            msg = c.poll(1.0)  # Wait for up to 1.0 seconds for a message

            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            if msg.value() is None:
                continue  # Tombstone message for key that was deleted
            else:
                # Process message
                handler.handle_message(msg)

        except KeyboardInterrupt:
            break

    c.close()
