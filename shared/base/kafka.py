import logging

from aiokafka import ConsumerRecord
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


def read_message[Scheme: BaseModel](record: ConsumerRecord[bytes, bytes], scheme: type[Scheme]) -> Scheme | None:
    """Read the message by the scheme or return none when it has no value or does not match the scheme."""
    value = record.value
    if value is None:
        logger.warning(f'Message without a value: {record}')
        return None
    try:
        return scheme.model_validate_json(value)
    except ValidationError as error:
        logger.warning(f'Message does not match {scheme.__name__}: {record}, {error}')
        return None
