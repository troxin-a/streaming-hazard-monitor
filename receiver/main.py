from contextlib import asynccontextmanager
from typing import AsyncIterator, Any

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from receiver.producers import create_producer
from receiver.routers import telemetry_router
from receiver.sessions import TelemetrySession
from receiver.urls import telemetry_url
from shared.config.session import async_session_maker
from shared.config.settings import config

DEBUG: bool = config.app.DEBUG

SWAGGER_UI_SETTINGS = {
    'filter': True,
    'persistAuthorization': True,
    'deepLinking': True,
    'displayRequestDuration': True,
    'tryItOutEnabled': True,
    'syntaxHighlight': True,
    'operationsSorter': 'alpha',
}


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[dict[str, Any]]:
    """Keep the producer running while the application works."""
    async with async_session_maker() as session:
        devices = await TelemetrySession(session).get_devices()
    telemetry_producer = create_producer()
    await telemetry_producer.start()

    yield {
        'telemetry_producer': telemetry_producer,
        'devices': devices
    }

    await telemetry_producer.stop()


app = FastAPI(
    lifespan=lifespan,
    title='Open telemetry receiver',
    docs_url='/receiver/docs/',
    debug=DEBUG,
    swagger_ui_parameters=SWAGGER_UI_SETTINGS,
)

app.include_router(telemetry_router, prefix=telemetry_url(), tags=['telemetry'])

add_pagination(app)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=[
        '*',
        'Access-Control-Allow-Origin',
        'Access-Control-Allow-Headers',
        'Access-Control-Allow-Credentials',
        'X-Amz-Date',
        'Access-Control-Request-Headers',
        'XMLHttpRequest',
        'accept',
        'authorization',
        'content-type',
        'user-agent',
        'x-requested-with',
    ],
)
