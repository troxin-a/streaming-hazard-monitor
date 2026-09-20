from starlette import status

from receiver.urls import telemetry_url
from shared.base.responses import responses
from shared.base.router import FastAPIRouter

telemetry_router = FastAPIRouter()


@telemetry_router.post(
    telemetry_url.telemetry,
    response_model=dict,
    responses=responses(
        dict,
        response_status=status.HTTP_202_ACCEPTED,
        statuses=[status.HTTP_202_ACCEPTED],
),
    status_code=status.HTTP_202_ACCEPTED,
    description='Send telemetry',
)
async def send_telemetry(
) -> dict:
    """Send telemetry."""
    return {}
