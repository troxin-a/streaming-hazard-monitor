from datetime import datetime, UTC
from uuid import UUID

from aiokafka import AIOKafkaProducer
from fastapi import Depends
from starlette import status

from receiver.auth import current_device_uuid
from receiver.producers import get_producer, send_reading
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
    await send_reading(producer, reading)
    return reading
