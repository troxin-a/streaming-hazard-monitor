from datetime import datetime, UTC
from uuid import UUID

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from fastapi import Depends, HTTPException
from starlette import status

from receiver.auth import current_device_uuid
from receiver.producer import get_producer, send_reading
from receiver.urls import telemetry_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter
from shared.reading.schemes import ReadingCreateScheme, ReadingMessageScheme

telemetry_router = FastAPIRouter()


@telemetry_router.post(
    telemetry_url.telemetry,
    response_model=ReadingMessageScheme,
    responses=responses(
        ReadingMessageScheme,
        response_status=status.HTTP_202_ACCEPTED,
        statuses=[status.HTTP_503_SERVICE_UNAVAILABLE],
        exclude=[status.HTTP_403_FORBIDDEN],
    ),
    status_code=status.HTTP_202_ACCEPTED,
    description='Send telemetry',
)
async def send_telemetry(
        body: ReadingCreateScheme,
        producer: AIOKafkaProducer = Depends(get_producer),
        device_uuid: UUID = Depends(current_device_uuid),
) -> ReadingMessageScheme:
    """Send the reading of the device to the readings topic."""
    reading = ReadingMessageScheme(device_uuid=device_uuid, value=body.value, received_at=datetime.now(UTC))
    try:
        await send_reading(producer, reading)
    except KafkaError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Broker is unavailable')
    return reading
