"""Модуль с исключениями для сущности Autoservice."""

from products.exceptions.base import BaseCustomError


class AutoserviceNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем автосервисе."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AutoserviceUserNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем пользователе автосервисе."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AutoserviceUserDoesntHavePermissionsError(BaseCustomError):
    """Исключение, возникающее при недостатке прав у пользователя автосервиса."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
