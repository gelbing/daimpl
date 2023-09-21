import logging
import os
import socket
import time
from typing import Protocol

from confluent_kafka import Consumer, KafkaError, KafkaException
from handler import Handler, LWWStrategy_Client

CLIENT_ID = os.environ.get("CLIENT_ID")
logging.basicConfig(level=logging.INFO)


class MessageHandler(Protocol):
    def handle_message(self, msg):
        pass


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


def sync_consumer(bootstrap_servers: str, server_topic: str, handler: MessageHandler):
    wait_for_kafka(bootstrap_servers)
    conf = {
        "bootstrap.servers": bootstrap_servers,
        "group.id": str(CLIENT_ID),
        "auto.offset.reset": "earliest",  # Start from the beginning if no offset is committed
        "enable.auto.commit": True,  # Commit offsets automatically
    }

    consumer = Consumer(conf)

    while True:
        try:
            consumer.subscribe([server_topic])

            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logging.info("Reached end of topic. Client is Up2Date")
                    if msg.error():
                        raise KafkaException(msg.error())
                if msg.value() is None:
                    continue  # Tombstone message for key that was deleted
                else:
                    handler.handle_message(msg)

        except Exception as e:
            print("Error:", e)
            print("Trying to reconnect...")
            time.sleep(5)  # Wait for 5 seconds before trying to reconnect


if __name__ == "__main__":
    lww_strategy_client = LWWStrategy_Client()
    lww_handler_client = Handler(lww_strategy_client)

    sync_consumer(
        bootstrap_servers="kafka:9092",
        server_topic="server-topic.public.todos",
        handler=lww_handler_client,
    )
