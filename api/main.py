from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from api.auth.routers import auth_router
from api.auth.urls import auth_url
from api.building.routers import building_router
from api.building.urls import building_url
from api.company.routers import company_router
from api.company.urls import company_url
from api.user.routers import user_router
from api.user.urls import user_url
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
    title='Streaming hazard monitor',
    docs_url='/api/docs/',
    debug=DEBUG,
    swagger_ui_parameters=SWAGGER_UI_SETTINGS,
)

app.include_router(auth_router, prefix=auth_url(), tags=['auth'])
app.include_router(user_router, prefix=user_url(), tags=['user'])
app.include_router(company_router, prefix=company_url(), tags=['company'])
app.include_router(building_router, prefix=building_url(), tags=['building'])

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
