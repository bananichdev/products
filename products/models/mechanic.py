# ruff: noqa: PLR2004
"""Модуль с моделями сущности Mechanic."""

from datetime import datetime
from typing import TYPE_CHECKING, Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig, dto_field
from litestar.exceptions import ClientException
from sqlalchemy import REAL, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from uuid_utils.compat import uuid7

if TYPE_CHECKING:
    from products.models.autoservice import Autoservice
    from products.models.maintenance import ProvidedMaintenance

mechanic_autoservice_association = Table(
    "mechanic_autoservice_association",
    AdvancedDeclarativeBase.metadata,
    Column("mechanic_id", ForeignKey("mechanics.mechanic_id"), primary_key=True),
    Column("autoservice_id", ForeignKey("autoservices.autoservice_id"), primary_key=True),
)
"""
Модель для связи многие-ко-многим сущности Mechanic и Autoservice. Показывает автосервисы, в которых работает механик.
"""


class Mechanic(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модель сущности Mechanic."""

    __tablename__ = "mechanics"

    mechanic_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)

    city: Mapped[str] = mapped_column(String(200), nullable=False)

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    lon: Mapped[float | None] = mapped_column(REAL, nullable=True)
    """Долгота."""

    lat: Mapped[float | None] = mapped_column(REAL, nullable=True)
    """Широта."""

    private: Mapped[bool] = mapped_column(nullable=False)
    """Механик-частник или нет."""

    mobile: Mapped[bool] = mapped_column(nullable=False)
    """Выездной механик или нет."""

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

    autoservices: Mapped[list["Autoservice"]] = relationship(
        secondary=mechanic_autoservice_association,
        lazy="noload",
        back_populates="mechanics",
        info=dto_field("read-only"),
    )

    provided_maintenance: Mapped[list["ProvidedMaintenance"]] = relationship(
        back_populates="mechanic",
        lazy="noload",
    )

    @validates("name")
    def validate_name(self, _: str, name: str) -> str:
        """Проверка имени на длину."""
        error_message: str | None = None
        if len(name) < 2:
            error_message = "Имя слишком короткое."
        elif len(name) > 150:
            error_message = "Имя слишком длинное."
        if error_message is not None:
            raise ClientException(error_message)
        return name

    @validates("description")
    def validate_description(self, _: str, description: str | None) -> str | None:
        """Проверка описания на длину."""
        if description is not None and len(description) > 1500:
            error_message = "Описание слишком длинное. Максимум - 1500 символов."
            raise ClientException(error_message)
        return description

    @validates("city")
    def validate_city(self, _: str, city: str) -> str:
        """Проверка названия города на длину."""
        if len(city) > 200:
            error_message = "Название города слишком длинное. Максимум - 200 символов."
            raise ClientException(error_message)
        return city

    @validates("address")
    def validate_address(self, _: str, address: str | None) -> str | None:
        """Проверка адреса на длину."""
        if address is not None and len(address) > 500:
            error_message = "Адрес слишком длинный. Максимум - 500 символов."
            raise ClientException(error_message)
        return address

    @validates("lon")
    def validate_lon(self, _: str, value: float | None) -> float | None:
        """Валидация долготы от -180 до 180."""
        if value is not None and (value < -180 or value > 180):
            error_message = "Долгота должна быть в диапазоне от -180.0 до 180.0"
            raise ClientException(error_message)
        return value

    @validates("lat")
    def validate_lat(self, _: str, value: float | None) -> float | None:
        """Валидация широты от -90 до 90."""
        if value is not None and (value < -90 or value > 90):
            error_message = "Широта должна быть в диапазоне от -90.0 до 90.0"
            raise ClientException(error_message)
        return value


MechanicPostDTO = SQLAlchemyDTO[
    Annotated[Mechanic, DTOConfig(exclude={"mechanic_id", "provided_maintenance"}, forbid_unknown_fields=True)]
]
MechanicPatchDTO = SQLAlchemyDTO[
    Annotated[
        Mechanic,
        DTOConfig(
            include={"name", "description", "city", "address", "lon", "lat", "private", "mobile"},
            partial=True,
            forbid_unknown_fields=True,
        ),
    ]
]
MechanicSimpleReturnDTO = SQLAlchemyDTO[
    Annotated[Mechanic, DTOConfig(exclude={"autoservices", "provided_maintenance"}, forbid_unknown_fields=True)]
]
