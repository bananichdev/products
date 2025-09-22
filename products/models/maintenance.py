# ruff: noqa: PLR2004
"""Модуль с моделями сущности Maintenance."""

from typing import TYPE_CHECKING, Annotated, Optional
from uuid import UUID

from advanced_alchemy.base import AdvancedDeclarativeBase, CommonTableAttributes
from advanced_alchemy.extensions.litestar import SQLAlchemyDTO
from litestar.dto import DTOConfig
from litestar.exceptions import ClientException
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, SmallInteger, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from uuid_utils.compat import uuid7

if TYPE_CHECKING:
    from products.models.autoservice import Autoservice
    from products.models.country import Country
    from products.models.mechanic import Mechanic
    from products.models.vehicle import VehicleBrand


class ProvidedMaintenanceCategory(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Категории услуг, предоставляемых автосервисами и механиками."""

    __tablename__ = "provided_maintenance_categories"

    provided_maintenance_category_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    provided_maintenance_types: Mapped[list["ProvidedMaintenanceType"]] = relationship(
        back_populates="provided_maintenance_category",
        lazy="raise",
    )

    @validates("name")
    def validate_name(self, _: str, value: str) -> str:
        """Валидация имени."""
        if len(value) > 100:
            error_message = "Название типа услуги не должно превышать 100 символов."
            raise ClientException(error_message)
        return value

    @validates("provided_maintenance_category_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class ProvidedMaintenanceType(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Типы услуг, предоставляемых автосервисами и механиками."""

    __tablename__ = "provided_maintenance_types"

    provided_maintenance_type_id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)

    provided_maintenance_category_id: Mapped[int] = mapped_column(
        ForeignKey(ProvidedMaintenanceCategory.provided_maintenance_category_id), nullable=False
    )

    provided_maintenance_category: Mapped[ProvidedMaintenanceCategory] = relationship(
        back_populates="provided_maintenance_types",
        lazy="raise",
    )

    provided_maintenance: Mapped[list["ProvidedMaintenance"]] = relationship(
        back_populates="provided_maintenance_type",
        lazy="raise",
    )

    @validates("name")
    def validate_name(self, _: str, value: str) -> str:
        """Валидация имени."""
        if len(value) > 200:
            error_message = "Название группы услуги не должно превышать 100 символов."
            raise ClientException(error_message)
        return value

    @validates("provided_maintenance_type_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class ProvidedMaintenanceCountryAssociation(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Связь многие-ко-многим между услугами и странами производителей.

    Показывает страны - производителей ТС, для которых доступна данная услуга.
    """

    __tablename__ = "provided_maintenance_country_association"

    provided_maintenance_id: Mapped[UUID] = mapped_column(
        ForeignKey("provided_maintenance.provided_maintenance_id"), primary_key=True
    )
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.country_id"), primary_key=True)

    @validates("country_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class ProvidedMaintenanceVehicleBrandAssociation(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Связь многие-ко-многим между услугами и марками транспортных средств.

    Показывает марки ТС, для которых доступна данная услуга.
    """

    __tablename__ = "provided_maintenance_vehicle_brand_association"

    provided_maintenance_id: Mapped[UUID] = mapped_column(
        ForeignKey("provided_maintenance.provided_maintenance_id"), primary_key=True
    )
    vehicle_brand_id: Mapped[int] = mapped_column(ForeignKey("vehicle_brands.vehicle_brand_id"), primary_key=True)

    @validates("vehicle_brand_id")
    def validate_country_id(self, _: str, value: int) -> int:
        """Валидация id страны."""
        if value > 32767:
            error_message = "ID страны не должно превышать 32767."
            raise ClientException(error_message)
        return value


class ProvidedMaintenance(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
    """Услуги, предоставляемые автосервисами и механиками."""

    __tablename__ = "provided_maintenance"

    provided_maintenance_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)

    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True, default=None)

    # Связи с типами услуг

    provided_maintenance_type_id: Mapped[int] = mapped_column(
        ForeignKey(ProvidedMaintenanceType.provided_maintenance_type_id), nullable=False
    )

    provided_maintenance_type: Mapped[ProvidedMaintenanceType] = relationship(
        back_populates="provided_maintenance",
        lazy="selectin",
    )

    # Связи с исполнителями

    mechanic_id: Mapped[UUID | None] = mapped_column(ForeignKey("mechanics.mechanic_id"), nullable=True)

    mechanic: Mapped[Optional["Mechanic"]] = relationship(
        back_populates="provided_maintenance",
        lazy="selectin",
    )

    autoservice_id: Mapped[UUID | None] = mapped_column(ForeignKey("autoservices.autoservice_id"), nullable=True)

    autoservice: Mapped[Optional["Autoservice"]] = relationship(
        back_populates="provided_maintenance",
        lazy="selectin",
    )

    # Связи со странами-производителями и марками ТС

    countries: Mapped[list["Country"]] = relationship(
        secondary=ProvidedMaintenanceCountryAssociation.__table__,
        lazy="selectin",
    )
    vehicle_brands: Mapped[list["VehicleBrand"]] = relationship(
        secondary=ProvidedMaintenanceVehicleBrandAssociation.__table__,
        lazy="selectin",
    )

    __table_args__ = (
        CheckConstraint("mechanic_id IS NOT NULL OR autoservice_id IS NOT NULL", name="check_mechanic_or_autoservice"),
    )


ProvidedMaintenancePostDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenance,
        DTOConfig(
            exclude={
                "provided_maintenance_id",
                "provided_maintenance_type",
                "mechanic",
                "autoservice",
                "countries",
                "vehicle_brands",
            },
            forbid_unknown_fields=True,
        ),
    ]
]
ProvidedMaintenanceCountryAssociationPostDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenanceCountryAssociation,
        DTOConfig(
            forbid_unknown_fields=True,
        ),
    ]
]
ProvidedMaintenanceCountryAssociationReturnDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenanceCountryAssociation,
        DTOConfig(
            forbid_unknown_fields=True,
        ),
    ]
]
ProvidedMaintenanceVehicleBrandAssociationPostDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenanceVehicleBrandAssociation,
        DTOConfig(
            forbid_unknown_fields=True,
        ),
    ]
]
ProvidedMaintenanceVehicleBrandAssociationReturnDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenanceVehicleBrandAssociation,
        DTOConfig(
            forbid_unknown_fields=True,
        ),
    ]
]
ProvidedMaintenanceReturnDTO = SQLAlchemyDTO[
    Annotated[
        ProvidedMaintenance,
        DTOConfig(
            exclude={"provided_maintenance_type_id", "mechanic_id", "autoservice_id"}, forbid_unknown_fields=True
        ),
    ]
]


# class Maintenance(AdvancedDeclarativeBase, CommonTableAttributes, AsyncAttrs):
#     """Сущность Maintenance.
#         Услуга, которую оказывает определенный Mechanic и/или
#         Autoservice определенному Customer в рамках определенной MaintenanceAppointment.
#     """
#
#     __tablename__ = "maintenance"
#
#     maintenance_id: Mapped[UUID] = mapped_column(default=uuid7, primary_key=True)
