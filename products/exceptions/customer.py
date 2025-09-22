"""Модуль с исключениями для сущности Vehicle."""

from products.exceptions.base import BaseCustomError


class CustomerNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем клиенте."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class CustomerBelongsToAnotherUserError(BaseCustomError):
    """Исключение, возникающее при попытке получить доступ к сущности владельца ТС другим пользователем."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
