"""Модуль с моделями сущности Country."""

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from sqlalchemy import SmallInteger
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column


class Country(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модель сущности Country."""

    __tablename__ = "countries"

    country_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(nullable=False, unique=True)
