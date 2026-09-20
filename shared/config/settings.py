import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent
dot_env = os.path.join(BASE_DIR, '.env')


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=dot_env,
        env_file_encoding='utf-8',
        extra='ignore',
    )


class AppSettings(EnvSettings):
    DEBUG: bool = False
    ENV_TYPE: str = 'dev'
    BACK_URL: str = '127.0.0.1'
    FRONT_URL: str = '127.0.0.1'


class JWTSettings(EnvSettings):
    SECRET_KEY: str = 'secret_key'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES_REMEMBER: int = 60 * 24 * 7


class DatabaseSettings(EnvSettings):
    POSTGRES_DB: str
    POSTGRES_TEST_DB: str = 'test_db'
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._database_url = None

    @property
    def database_url(self):
        """URL database Postgres."""
        if self._database_url is not None:
            return self._database_url
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:'
                f'{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    @database_url.setter
    def database_url(self, value):
        """Setter of database url."""
        self._database_url = value

    def get_test_db_url(self, name: str) -> str:
        user, passwd = self.POSTGRES_USER, self.POSTGRES_PASSWORD
        host, port = self.POSTGRES_HOST, self.POSTGRES_PORT
        return f'postgresql+asyncpg://{user}:{passwd}@{host}:{port}/{name}'

    @property
    def root_database_url(self):
        """URL root database."""
        return self.get_test_db_url('postgres')

    @property
    def test_database_url(self):
        """URL test's database."""
        return self.get_test_db_url(self.POSTGRES_TEST_DB)

    @property
    def test_sqlite_db_url(self):
        """URL of test SQLite database."""
        return 'sqlite+aiosqlite:///:memory:'

    @property
    def is_sqlite(self):
        """Check database driver name."""
        database_url = self.database_url
        db_url = make_url(database_url)
        return db_url.drivername == 'sqlite+aiosqlite'

    @property
    def is_psql(self):
        """Check database driver name."""
        database_url = self.database_url
        db_url = make_url(database_url)
        return db_url.drivername == 'postgresql+asyncpg'


# class CelerySettings(EnvSettings):
#     CELERY_BROKER_URL: str
#     CELERY_RESULT_BACKEND: str
#
#
# class RedisSettings(EnvSettings):
#     REDIS_HOST: str
#     REDIS_PORT: str
#
#     @property
#     def redis_url(self):
#         """Redis URL."""
#         return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'


class Config(EnvSettings):
    app: AppSettings = AppSettings()
    jwt: JWTSettings = JWTSettings()
    database: DatabaseSettings = DatabaseSettings()
    # celery: CelerySettings = CelerySettings()
    # redis: RedisSettings = RedisSettings()


config = Config()
