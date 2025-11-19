from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

from src.auth.routers import auth_router
from src.auth.urls import auth_url
from src.config.settings import config
from src.user.routers import user_router
from src.user.urls import user_url

DEBUG: bool = config.app.DEBUG

app = FastAPI(title='Tic-tac-toe game', debug=DEBUG)

app.include_router(auth_router, prefix=auth_url(), tags=['auth'])
app.include_router(user_router, prefix=user_url(), tags=['user'])

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
