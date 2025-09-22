"""Модуль для запуска сервера."""

from granian import Granian
from granian.constants import Interfaces

from products.settings import LoggingSettings, ServerSettings, provide_logging_settings, provide_server_settings


def main(server_settings: ServerSettings, logging_settings: LoggingSettings) -> None:
    """Точка входа в приложение."""
    server = Granian(
        target="products.app:provide_app",
        factory=True,
        address=server_settings.host,
        port=server_settings.port,
        reload=logging_settings.env == "local",
        interface=Interfaces.ASGI,
        log_dictconfig=logging_settings.granian_log_dictconfig,
        log_access=True,
    )
    server.serve()


if __name__ == "__main__":
    __server_settings = provide_server_settings()
    __logging_settings = provide_logging_settings()
    main(server_settings=__server_settings, logging_settings=__logging_settings)
