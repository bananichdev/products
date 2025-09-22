"""Модуль с HTTP-исключениями."""

from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_409_CONFLICT


class ConflictException(HTTPException):
    """Конфликт."""

    status_code = HTTP_409_CONFLICT
