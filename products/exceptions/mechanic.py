"""Модуль с исключениями для сущности Mechanic."""

from products.exceptions.base import BaseCustomError


class MechanicNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем механике."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class MechanicBelongsToAnotherUserError(BaseCustomError):
    """Исключение, возникающее при попытке получить доступ к сущности механика другим пользователем."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
