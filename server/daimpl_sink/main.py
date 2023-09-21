import logging

from consumer import consume_kafka_messages
from handler import Handler, LWWStrategy_Server
import os

BOOTSTRAP_SERVERS = os.environ.get("BOOTSTRAP_SERVERS")
NUM_CLIENTS = os.environ.get("NUM_CLIENTS")

CLIENT_TOPICS = [f"client-{i}-topic.public.todos" for i in range(1, int(NUM_CLIENTS) + 1)]


# Set loglevel to INFO to see less logs
logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)


def main():
    lww_strategy = LWWStrategy_Server()
    lww_handler = Handler(lww_strategy)


    consume_kafka_messages(
        BOOTSTRAP_SERVERS,
        CLIENT_TOPICS,
        lww_handler,
    )


if __name__ == "__main__":
    main()
