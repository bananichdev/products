"""Модуль с исключениями для сущности Country."""

from products.exceptions.base import BaseCustomError


class CountryNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующей стране."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
