"""Модуль настроек."""

from typing import Literal

from advanced_alchemy.config import AlembicAsyncConfig
from advanced_alchemy.extensions.litestar import (
    AsyncSessionConfig,
    EngineConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from general_settings import (
    GeneralAppSettings,
    GeneralAuthSettings,
    GeneralDatabaseSettings,
    GeneralLoggingSettings,
    GeneralServerSettings,
)
from litestar.logging import StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.openapi import OpenAPIConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from litestar.stores.redis import RedisStore
from litestar.types import Logger
from litestar_utils.middlewares.logging import LoggingRequestMiddleware
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from structlog import PrintLoggerFactory

from products.__version__ import __version__


class AppSettings(GeneralAppSettings):
    """Настройки приложения."""

    app_name: str = "products"


class AuthSettings(GeneralAuthSettings):
    """Настройки Auth."""

    basic_auth_header_key: str = "Authorization"


class DatabaseSettings(GeneralDatabaseSettings):
    """Настройки базы данных."""

    db_user: str = "admin"
    db_password: SecretStr = SecretStr("admin")
    db_name: str = "products"

    before_send_handler: Literal["autocommit", "autocommit_include_redirects"] = "autocommit"
    engine_dependency_key: str = "db_engine"
    session_dependency_key: str = "db_session"
    engine_app_state_key: str = "db_engine"
    session_maker_app_state_key: str = "session_maker_class"


class RedisSettings(BaseSettings):
    """Настройки Redis."""

    model_config = SettingsConfigDict(env_prefix="redis_")
    url: str = "redis://localhost:6379"
    db: int | None = None
    port: int | None = None
    username: str | None = None
    password: str | None = None


class ServerSettings(GeneralServerSettings):
    """Настройки сервера."""

    host: str = "127.0.0.1"
    port: int = 8443


class LoggingSettings(GeneralLoggingSettings):
    """Настройки логирования."""


def provide_app_settings() -> AppSettings:
    """Возвращает настройки приложения."""
    return AppSettings()


def provide_auth_settings() -> AuthSettings:
    """Возвращает Auth настройки."""
    return AuthSettings()


def provide_database_settings() -> DatabaseSettings:
    """Возвращает DatabaseSettings."""
    return DatabaseSettings()


def provide_server_settings() -> ServerSettings:
    """Возвращает ServerSettings."""
    return ServerSettings()


def provide_logging_settings() -> LoggingSettings:
    """Возвращает LoggingSettings."""
    return LoggingSettings()


def provide_sqlalchemy_init_plugin(database_settings: DatabaseSettings) -> SQLAlchemyInitPlugin:
    """Возвращает плагин SQLAlchemy."""
    session_config = AsyncSessionConfig(
        expire_on_commit=database_settings.expire_on_commit,
        autoflush=database_settings.autoflush,
        join_transaction_mode=database_settings.join_transaction_mode,
    )
    engine_config = EngineConfig(
        pool_size=database_settings.pool_size,
        max_overflow=database_settings.max_overflow,
        pool_recycle=database_settings.pool_recycle,
        pool_pre_ping=database_settings.pool_pre_ping,
        echo=database_settings.echo,
        insertmanyvalues_page_size=database_settings.insertmanyvalues_page_size,
    )
    alembic_config = AlembicAsyncConfig(
        toml_file="pyproject.toml",
    )
    sqlalchemy_config = SQLAlchemyAsyncConfig(
        connection_string=database_settings.db_full_url,
        before_send_handler=database_settings.before_send_handler,
        session_config=session_config,
        engine_config=engine_config,
        alembic_config=alembic_config,
        engine_dependency_key=database_settings.engine_dependency_key,
        session_dependency_key=database_settings.session_dependency_key,
        engine_app_state_key=database_settings.engine_app_state_key,
        session_maker_app_state_key=database_settings.session_maker_app_state_key,
    )
    return SQLAlchemyInitPlugin(config=sqlalchemy_config)


def provide_structlog_logging_config(logging_settings: LoggingSettings) -> StructLoggingConfig:
    """Возвращает StructLoggingConfig."""
    return StructLoggingConfig(processors=logging_settings.processors, logger_factory=PrintLoggerFactory())


def provide_structlog_plugin(logging_settings: LoggingSettings, auth_settings: AuthSettings) -> StructlogPlugin:
    """Возвращает StructlogPlugin."""
    structlog_logging_config = provide_structlog_logging_config(logging_settings=logging_settings)
    middleware_logging_config = LoggingMiddlewareConfig(
        request_cookies_to_obfuscate={auth_settings.jwt_token_cookie_key},
        request_headers_to_obfuscate={
            auth_settings.jwt_token_header_key,
            auth_settings.basic_auth_header_key,
            "cookie",
        },
        response_cookies_to_obfuscate={auth_settings.jwt_token_cookie_key},
        response_headers_to_obfuscate={
            auth_settings.jwt_token_header_key,
            auth_settings.basic_auth_header_key,
            "cookie",
        },
        middleware_class=LoggingRequestMiddleware,
    )
    structlog_config = StructlogConfig(
        structlog_logging_config=structlog_logging_config,
        middleware_logging_config=middleware_logging_config,
    )
    return StructlogPlugin(config=structlog_config)


def provide_openapi_config(app_settings: AppSettings) -> OpenAPIConfig:
    """Возвращает конфигурацию OpenAPI."""
    return OpenAPIConfig(
        title=app_settings.app_name,
        version=__version__,
        create_examples=True,
    )


def provide_redis_store(redis_settings: RedisSettings) -> RedisStore:
    """Возвращает RedisStore."""
    return RedisStore.with_client(
        url=redis_settings.url,
        db=redis_settings.db,
        port=redis_settings.port,
        username=redis_settings.username,
        password=redis_settings.password,
    )


def provide_redis_settings() -> RedisSettings:
    """Возвращает настройки Redis."""
    return RedisSettings()


def provide_blacklist_store(redis_store: RedisStore) -> RedisStore:
    """Возвращает Blacklist RedisStore."""
    return redis_store.with_namespace("blacklist_store")


__logging_settings: LoggingSettings = provide_logging_settings()
__logging_config: StructLoggingConfig = provide_structlog_logging_config(logging_settings=__logging_settings)
logger: Logger = __logging_config.configure()()
