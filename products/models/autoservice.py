# ruff: noqa: PLR2004
"""Модуль с моделями сущности Autoservice."""

from datetime import datetime
from enum import Enum
from re import match
from typing import TYPE_CHECKING, Annotated
from uuid import UUID
from zoneinfo import ZoneInfo

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig, dto_field
from litestar.exceptions import ClientException
from sqlalchemy import ARRAY, REAL, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from uuid_utils.compat import uuid7

from products.models.mechanic import mechanic_autoservice_association

if TYPE_CHECKING:
    from products.models.maintenance import ProvidedMaintenance
    from products.models.mechanic import Mechanic


class AutoserviceUserPermissions(Enum):
    """Разрешения пользователей в автосервисе."""

    autoservice_manage = "autoservice:manage"
    """Разрешение на управление автосервисом (изменение данных, удаление)."""

    autoservice_manage_provided_maintenance = "autoservice:manage_provided_maintenance"
    """Разрешение на управление обслуживаниями, которые предоставляет автосервис."""


class AutoserviceUser(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Связь пользователей с автосервисами и их ролями."""

    __tablename__ = "autoservice_users"

    uid: Mapped[UUID] = mapped_column(primary_key=True)

    autoservice_id: Mapped[UUID] = mapped_column(ForeignKey("autoservices.autoservice_id"), primary_key=True)

    autoservice: Mapped["Autoservice"] = relationship(
        back_populates="users",
        lazy="noload",
    )

    permissions: Mapped[list[AutoserviceUserPermissions]] = mapped_column(
        ARRAY(ENUM(AutoserviceUserPermissions, values_callable=lambda enum: [e.value for e in enum])),
        nullable=False,
        default=[],
    )


class Autoservice(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модель сущности Autoservice."""

    __tablename__ = "autoservices"

    autoservice_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)

    description: Mapped[str | None] = mapped_column(String(1500), nullable=True)

    itn: Mapped[str] = mapped_column(String(12), nullable=False)

    psrn: Mapped[str] = mapped_column(String(13), nullable=False)

    city: Mapped[str] = mapped_column(String(200), default="", nullable=False)

    address: Mapped[str] = mapped_column(String(500), nullable=False)

    lon: Mapped[float | None] = mapped_column(REAL, nullable=True)
    """Долгота."""

    lat: Mapped[float | None] = mapped_column(REAL, nullable=True)
    """Широта."""

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, info=dto_field("read-only")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(ZoneInfo("Europe/Moscow")),
        info=dto_field("read-only"),
    )

    mechanics: Mapped[list["Mechanic"]] = relationship(
        secondary=mechanic_autoservice_association,
        lazy="noload",
        back_populates="autoservices",
        info=dto_field("read-only"),
    )

    users: Mapped[list[AutoserviceUser]] = relationship(
        back_populates="autoservice",
        lazy="noload",
    )

    provided_maintenance: Mapped[list["ProvidedMaintenance"]] = relationship(
        back_populates="autoservice",
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
    def validate_address(self, _: str, address: str) -> str:
        """Проверка адреса на длину."""
        if len(address) > 500:
            error_message = "Адрес слишком длинный. Максимум - 500 символов."
            raise ClientException(error_message)
        return address

    @validates("itn")
    def validate_itn(self, _: str, value: str) -> str:
        """Валидация ИНН от 10 до 12 цифр."""
        if not match(r"^\d{10}(\d{2})?$", value):
            error_message = "ИНН должен содержать 10 или 12 цифр"
            raise ClientException(error_message)
        return value

    @validates("psrn")
    def validate_psrn(self, _: str, value: str) -> str:
        """Валидация ОГРН ровно 13 цифр."""
        if not match(r"^\d{13}$", value):
            error_message = "ОГРН должен содержать ровно 13 цифр"
            raise ClientException(error_message)
        return value

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


AutoservicePostDTO = SQLAlchemyDTO[
    Annotated[
        Autoservice, DTOConfig(exclude={"autoservice_id", "users", "provided_maintenance"}, forbid_unknown_fields=True)
    ]
]
AutoservicePatchDTO = SQLAlchemyDTO[
    Annotated[
        Autoservice,
        DTOConfig(
            include={"name", "description"},
            partial=True,
            forbid_unknown_fields=True,
        ),
    ]
]
AutoserviceGetListDTO = SQLAlchemyDTO[
    Annotated[Autoservice, DTOConfig(include={"name", "city"}, forbid_unknown_fields=True)]
]
AutoserviceSimpleReturnDTO = SQLAlchemyDTO[
    Annotated[
        Autoservice, DTOConfig(exclude={"mechanics", "users", "provided_maintenance"}, forbid_unknown_fields=True)
    ]
]
