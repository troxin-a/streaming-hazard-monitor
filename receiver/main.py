from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from receiver.routers import telemetry_router
from receiver.urls import telemetry_url
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

app = FastAPI(
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
