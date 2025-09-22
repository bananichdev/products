"""Модель сущности User."""

from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    """Сущность User."""

    uid: UUID
