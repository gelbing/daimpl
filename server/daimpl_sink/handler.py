import json
import logging
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, Tuple

from confluent_kafka import Message
from crud import CRUDTodo
from engine import get_db
from models import TodoORM as TodoORM
from schemas import Todo, TodoCreate, TodoUpdate

crud_todo = CRUDTodo(TodoORM)


class AbstractStrategy(ABC):
    @abstractmethod
    def handle_create(self, msg: Tuple[Dict, Dict]):
        pass

    @abstractmethod
    def handle_update(self, msg: Tuple[Dict, Dict]):
        pass

    @abstractmethod
    def handle_delete(self, msg: Tuple[Dict, Dict]):
        pass


class LWWStrategy_Server(AbstractStrategy):
    """LWWStrategy implements the Last-Write-Wins strategy for handling messages from the Kafka Consumer."""

    def handle_create(self, msg: Tuple[Dict, Dict]):
        logging.info("CREATE REQUEST")
        after_obj = msg[1].get("payload", {}).get("after", {})

        logging.debug(f"after_obj: {after_obj}")
        id = after_obj.get("id")
        client_id = after_obj.get("client_id")
        with get_db() as db:
            db_obj = crud_todo.get(db, id=id, client_id=client_id)
            if db_obj is not None:
                if Todo(**after_obj) == Todo.model_validate(db_obj):
                    logging.info("SYNC detected. Skipping...")
                    return
                else:
                    logging.warning("Unexpected conflict. Blocking create")
                    return
            else:
                logging.info("CREATING...")
                crud_todo.create(db, obj_in=TodoCreate(**after_obj))

    def handle_update(self, msg: Tuple[Dict, Dict]):
        logging.info("UPDATE REQUEST")
        todo_id = msg[0].get("payload", {}).get("id", {})
        client_id = msg[0].get("payload", {}).get("client_id", {})

        before_obj = msg[1].get("payload", {}).get("before", {})
        after_obj = msg[1].get("payload", {}).get("after", {})

        logging.debug(f"before_obj: {before_obj}")
        logging.debug(f"after_obj: {after_obj}")

        with get_db() as db:
            db_todo = crud_todo.get(db, id=todo_id, client_id=client_id)

            if db_todo is None:
                logging.info("UPDATE TO NON-EXISTENT ITEM. CREATE INSTEAD ...")
                return self.handle_create(msg)

            parsed_db_todo = Todo.model_validate(db_todo)
            parsed_before_obj = Todo.model_validate(before_obj)
            parsed_after_obj = Todo.model_validate(after_obj)

            if parsed_after_obj == parsed_db_todo:
                logging.info("SYNC detected. Skipping...")
                return
            elif parsed_before_obj == parsed_db_todo:
                logging.info("UPDATING...")
            else:
                logging.warning(
                    "CONFLICT. Before !== Server Item. UPDATING if after is newer..."
                )
                # ! We update anyways if the after item is new then the stored item (Last Writer Wins)

            if parsed_after_obj.updated_at > parsed_db_todo.updated_at:
                crud_todo.update(db, db_obj=db_todo, obj_in=TodoUpdate(**after_obj))
            else:
                logging.info(
                    "After is not newer than the server instance. Skipping update."
                )

    def handle_delete(self, msg: Tuple[Dict, Dict]):
        logging.info("DELETE REQUEST")
        todo_id = msg[0].get("payload", {}).get("id", {})
        client_id = msg[0].get("payload", {}).get("client_id", {})

        before_obj = msg[1].get("payload", {}).get("before", {})

        logging.debug(f"before_obj: {before_obj}")
        with get_db() as db:
            db_todo = crud_todo.get(db, id=todo_id, client_id=client_id)

            if db_todo is None:
                logging.info("SYNC detected. Skipping...")
                return

            parsed_db_todo = Todo.model_validate(db_todo)
            parsed_before_obj = Todo.model_validate(before_obj)

            if parsed_before_obj == parsed_db_todo:
                logging.info("DELETING ...")
                crud_todo.delete(db, id=todo_id, client_id=client_id)
            else:
                logging.warning("CONFLICT. Before !== Server Item. Deleting ...")
                crud_todo.delete(db, id=todo_id, client_id=client_id)
                return


class MsgType(Enum):
    """The Message Type represents the database operation that was performed by the client."""

    CREATE = auto()
    UPDATE = auto()
    DELETE = auto()


def derive_msg_type(msg_value: Dict) -> MsgType:
    """Get the Message Type based on the messages Value.

    Args:
        msg (Dict): A Debezium CDC Message

    Returns:
        MsgType: The Message Type

    """

    operation = msg_value.get("payload", {}).get("op")
    if operation is None:
        logging.error("Invalid message type, operation is None")
        raise ValueError("Invalid message type, operation is None")
    if operation == "c":
        logging.debug("CREATE message received")
        return MsgType.CREATE
    elif operation == "u":
        logging.debug("UPDATE message received")
        return MsgType.UPDATE
    elif operation == "d":
        logging.debug("DELETE message received")
        return MsgType.DELETE
    else:
        logging.error(f"Invalid message type, operation is {operation}")
        raise ValueError(f"Invalid message type, operation is {operation}")


class Handler:
    """The Handler class is responsible for handling messages from the Kafka Consumer."""

    def __init__(self, strategy: AbstractStrategy):
        self.strategy = strategy

    def handle_message(self, msg: Message):
        """Processes a message from the Kafka Consumer by calling the appropriate strategy method.

        Args:
            msg (Message): msg (Message): The Kafka (Confluent) Message


        """

        msk_key_str = msg.key().decode("utf-8")
        msk_key_object = json.loads(msk_key_str)

        msg_value_str = msg.value().decode("utf-8")
        msg_value_object = json.loads(msg_value_str)

        msg_type = derive_msg_type(msg_value_object)

        if msg_type == MsgType.CREATE:
            self.strategy.handle_create((msk_key_object, msg_value_object))
        elif msg_type == MsgType.UPDATE:
            self.strategy.handle_update((msk_key_object, msg_value_object))
        elif msg_type == MsgType.DELETE:
            self.strategy.handle_delete((msk_key_object, msg_value_object))
        else:
            logging.error(f"Invalid message type received: {msg_type}")
            raise ValueError(f"Invalid message type: {msg_type}")
