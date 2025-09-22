# ruff: noqa: PLR2004
"""Модуль с моделями сущности Customer."""

from datetime import datetime
from typing import TYPE_CHECKING, Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig, dto_field
from litestar.exceptions import ClientException
from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from uuid_utils.compat import uuid7

if TYPE_CHECKING:
    from products.models.vehicle import Vehicle


class Customer(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модель сущности Customer."""

    __tablename__ = "customers"

    customer_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    city: Mapped[str | None] = mapped_column(String(200), nullable=True)

    uid: Mapped[UUID] = mapped_column(nullable=False, unique=True, index=True, info=dto_field("read-only"))

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, info=dto_field("read-only")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(ZoneInfo("Europe/Moscow")),
        info=dto_field("read-only"),
    )

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="customer",
        lazy="noload",
    )

    @validates("name")
    def validate_name(self, _: str, name: str) -> str:
        """Проверка имени на длину."""
        error_message: str | None = None
        if len(name) < 2:
            error_message = "Имя слишком короткое. Минимум - 2 символа."
        elif len(name) > 150:
            error_message = "Имя слишком длинное. Максимум - 150 символов."
        if error_message is not None:
            raise ClientException(error_message)
        return name

    @validates("city")
    def validate_city(self, _: str, city: str | None) -> str | None:
        """Проверка названия города на длину."""
        if city is not None and len(city) > 200:
            error_message = "Название города слишком длинное. Максимум - 200 символов."
            raise ClientException(error_message)
        return city


CustomerPostDTO = SQLAlchemyDTO[
    Annotated[Customer, DTOConfig(exclude={"customer_id", "vehicles"}, forbid_unknown_fields=True)]
]
CustomerSimpleReturnDTO = SQLAlchemyDTO[
    Annotated[Customer, DTOConfig(exclude={"vehicles"}, forbid_unknown_fields=True)]
]
CustomerPatchDTO = SQLAlchemyDTO[
    Annotated[
        Customer,
        DTOConfig(
            include={"name", "city"},
            partial=True,
            forbid_unknown_fields=True,
        ),
    ]
]
