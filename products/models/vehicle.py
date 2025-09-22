# ruff: noqa: PLR2004
"""Модуль с сущностью Vehicle."""

from re import IGNORECASE, match, sub
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig, dto_field
from litestar.exceptions import ClientException
from sqlalchemy import ForeignKey, Integer, SmallInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from uuid_utils.compat import uuid7

from products.models.country import Country

if TYPE_CHECKING:
    from products.models.customer import Customer


class VehicleBrand(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Марки ТС."""

    __tablename__ = "vehicle_brands"

    vehicle_brand_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    popular: Mapped[bool] = mapped_column(nullable=False, default=False, info=dto_field("private"))

    country_id: Mapped[int] = mapped_column(ForeignKey(Country.country_id), nullable=False)

    country: Mapped[Country] = relationship(
        lazy="raise",
    )

    vehicle_models: Mapped[list["VehicleModel"]] = relationship(
        back_populates="vehicle_brand",
        lazy="raise",
    )

    @validates("vehicle_brand_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class VehicleModel(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модели ТС."""

    __tablename__ = "vehicle_models"

    vehicle_model_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    vehicle_brand_id: Mapped[int] = mapped_column(ForeignKey(VehicleBrand.vehicle_brand_id), nullable=False)

    vehicle_brand: Mapped[VehicleBrand] = relationship(
        back_populates="vehicle_models",
        lazy="raise",
    )

    vehicle_generations: Mapped[list["VehicleGeneration"]] = relationship(
        back_populates="vehicle_model",
        lazy="raise",
    )

    @validates("vehicle_brand_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class VehicleGeneration(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Поколение ТС."""

    __tablename__ = "vehicle_generations"

    vehicle_generation_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)

    start_year_production: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    end_year_production: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    vehicle_model_id: Mapped[int] = mapped_column(ForeignKey(VehicleModel.vehicle_model_id), nullable=False)

    vehicle_model: Mapped[VehicleModel] = relationship(
        back_populates="vehicle_generations",
        lazy="raise",
    )


class Vehicle(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Модель сущности Vehicle."""

    __tablename__ = "vehicles"

    vehicle_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)

    state_number: Mapped[str | None] = mapped_column(String(12), nullable=True)

    vin: Mapped[str | None] = mapped_column(String(17), nullable=True, unique=True)

    vehicle_brand_id: Mapped[int] = mapped_column(ForeignKey(VehicleBrand.vehicle_brand_id), nullable=False)

    vehicle_brand: Mapped[VehicleBrand] = relationship(
        lazy="selectin",
    )

    vehicle_model_id: Mapped[int] = mapped_column(ForeignKey(VehicleModel.vehicle_model_id), nullable=False)

    vehicle_model: Mapped[VehicleModel] = relationship(
        lazy="selectin",
    )

    vehicle_generation_id: Mapped[int] = mapped_column(
        ForeignKey(VehicleGeneration.vehicle_generation_id), nullable=False
    )

    vehicle_generation: Mapped[VehicleGeneration] = relationship(
        lazy="selectin",
    )

    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.customer_id"), nullable=False)

    customer: Mapped["Customer"] = relationship(
        back_populates="vehicles",
        lazy="raise",
    )

    @validates("vin")
    def validate_vin(self, _: str, vin: str | None) -> str | None:
        """Валидация VIN номера."""
        if vin is None:
            return None
        vin = sub(r"\s+", "", vin).upper()
        if not match(r"^[A-HJ-NPR-Z0-9]{17}$", vin):
            error_message = (
                "Неверный формат VIN. Требования: "
                "ровно 17 символов (цифры и заглавные латинские буквы), "
                "запрещены буквы I, O, Q"
            )
            raise ClientException(error_message)
        return vin

    @validates("state_number")
    def validate_state_number(self, _: str, state_number: str | None) -> str | None:
        """Валидация гос. номера."""
        if state_number is None:
            return None
        state_number = sub(r"\s+", "", state_number).upper()
        patterns = (
            r"^[АВЕКМНОРСТУХABEKMHOPCTYX]\d{3}(?<!000)[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$",  # Стандарт
            r"^[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{3}(?<!000)\d{2,3}$",  # Такси
            r"^\d{4}(?<!0000)[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$",  # Мотоциклы
            r"^[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{3}(?<!000)[АВЕКМНОРСТУХABEKMHOPCTYX]\d{2,3}$",  # Транзитные номера
            r"^Т[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{3}(?<!000)\d{2,3}$",  # Выездные/временные номера
            r"^[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{4}$",  # Прицепы
            r"^\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$",  # Дипломатические
        )
        if len(state_number) < 8 or len(state_number) > 12:
            error_message = "Недопустимая длина гос. номера. Должно быть 8-12 символов."
            raise ClientException(error_message)
        for pattern in patterns:
            if match(pattern, state_number, IGNORECASE):
                return state_number
        error_message = "Неверный формат государственного номера."
        raise ClientException(error_message)


VehiclePostDTO = SQLAlchemyDTO[
    Annotated[
        Vehicle,
        DTOConfig(
            exclude={"vehicle_id", "vehicle_brand", "vehicle_model", "vehicle_generation", "customer"},
            forbid_unknown_fields=True,
        ),
    ]
]
VehicleSimpleReturnDTO = SQLAlchemyDTO[
    Annotated[
        Vehicle,
        DTOConfig(
            exclude={
                "vehicle_brand_id",
                "vehicle_model_id",
                "vehicle_model.vehicle_brand_id",
                "vehicle_generation_id",
                "vehicle_generation.vehicle_model_id",
                "customer",
            },
            forbid_unknown_fields=True,
        ),
    ]
]
