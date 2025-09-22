"""Модуль с сервисами сущности Maintenance и связанными с ней сущностями."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.maintenance import (
    ProvidedMaintenanceCountryAssociationAlreadyExistsError,
    ProvidedMaintenanceCountryAssociationNotFoundError,
    ProvidedMaintenanceNotFoundError,
    ProvidedMaintenanceTypeNotFoundError,
    ProvidedMaintenanceVehicleBrandAssociationAlreadyExistsError,
)
from products.exceptions.mechanic import MechanicBelongsToAnotherUserError
from products.models.maintenance import (
    ProvidedMaintenance,
    ProvidedMaintenanceCategory,
    ProvidedMaintenanceCountryAssociation,
    ProvidedMaintenanceType,
    ProvidedMaintenanceVehicleBrandAssociation,
)
from products.models.user import User
from products.services.autoservice import AutoserviceService
from products.services.country import CountryService
from products.services.mechanic import MechanicService
from products.services.vehicle import VehicleBrandService
from products.settings import logger

if TYPE_CHECKING:
    from products.models.autoservice import Autoservice
    from products.models.mechanic import Mechanic


class ProvidedMaintenanceCategoryRepository(SQLAlchemyAsyncRepository[ProvidedMaintenanceCategory]):  # type: ignore[type-var]
    """ProvidedMaintenanceCategoryRepository для взаимодействия с БД."""

    id_attribute = "provided_maintenance_category_id"
    model_type = ProvidedMaintenanceCategory


class ProvidedMaintenanceCategoryService(SQLAlchemyAsyncRepositoryService[ProvidedMaintenanceCategory]):  # type: ignore[type-var]
    """ProvidedMaintenanceCategoryService для бизнес-логики."""

    repository_type = ProvidedMaintenanceCategoryRepository


async def provide_provided_maintenance_category_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProvidedMaintenanceCategoryService]:
    """Возвращает ProvidedMaintenanceCategoryService."""
    async with ProvidedMaintenanceCategoryService.new(session=db_session) as service:
        yield service


class ProvidedMaintenanceTypeRepository(SQLAlchemyAsyncRepository[ProvidedMaintenanceType]):  # type: ignore[type-var]
    """ProvidedMaintenanceTypeRepository для взаимодействия с БД."""

    id_attribute = "provided_maintenance_type_id"
    model_type = ProvidedMaintenanceType


class ProvidedMaintenanceTypeService(SQLAlchemyAsyncRepositoryService[ProvidedMaintenanceType]):  # type: ignore[type-var]
    """ProvidedMaintenanceTypeService для бизнес-логики."""

    repository_type = ProvidedMaintenanceTypeRepository

    async def get_provided_maintenance_type_by_provided_maintenance_id(
        self, provided_maintenance_type_id: int
    ) -> ProvidedMaintenanceType:
        """Получение ProvidedMaintenanceType по provided_maintenance_type_id."""
        if (
            provided_maintenance_type := await self.get_one_or_none(
                ProvidedMaintenanceType.provided_maintenance_type_id == provided_maintenance_type_id
            )
        ) is None:
            logger.warn(f"ProvidedMaintenanceType with {provided_maintenance_type_id=} doesn't exists in db")
            error_message = "Тип обслуживания не найден."
            raise ProvidedMaintenanceTypeNotFoundError(error_message)
        return provided_maintenance_type


async def provide_provided_maintenance_type_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProvidedMaintenanceTypeService]:
    """Возвращает ProvidedMaintenanceTypeService."""
    async with ProvidedMaintenanceTypeService.new(session=db_session) as service:
        yield service


class BaseProvidedMaintenanceRepository(SQLAlchemyAsyncRepository[ProvidedMaintenance]):  # type: ignore[type-var]
    """BaseProvidedMaintenanceRepository для взаимодействия с БД."""

    id_attribute = "provided_maintenance_id"
    model_type = ProvidedMaintenance


class BaseProvidedMaintenanceService(SQLAlchemyAsyncRepositoryService[ProvidedMaintenance]):  # type: ignore[type-var]
    """BaseProvidedMaintenanceService для бизнес-логики."""

    repository_type = BaseProvidedMaintenanceRepository

    async def get_provided_maintenance_by_provided_maintenance_id(
        self, provided_maintenance_id: UUID
    ) -> ProvidedMaintenance:
        """Получение ProvidedMaintenance по provided_maintenance_id."""
        if (
            provided_maintenance := await self.get_one_or_none(
                ProvidedMaintenance.provided_maintenance_id == provided_maintenance_id,
            )
        ) is None:
            logger.warn(f"ProvidedMaintenance with {provided_maintenance_id=} doesn't exists in db")
            error_message = "Предоставляемое обслуживание не найдено."
            raise ProvidedMaintenanceNotFoundError(error_message)
        logger.info(f"Got ProvidedMaintenance{provided_maintenance.to_dict()} from db")
        return provided_maintenance


async def provide_base_provided_maintenance_service(
    db_session: AsyncSession,
) -> AsyncGenerator[BaseProvidedMaintenanceService]:
    """Возвращает BaseProvidedMaintenanceService."""
    async with BaseProvidedMaintenanceService.new(session=db_session) as service:
        yield service


class ProvidedMaintenanceVehicleBrandAssociationRepository(
    SQLAlchemyAsyncRepository[ProvidedMaintenanceVehicleBrandAssociation]  # type: ignore[type-var]
):
    """ProvidedMaintenanceVehicleBrandAssociationRepository для взаимодействия с БД."""

    id_attribute = "provided_maintenance_id"
    model_type = ProvidedMaintenanceVehicleBrandAssociation


class ProvidedMaintenanceVehicleBrandAssociationService(
    SQLAlchemyAsyncRepositoryService[ProvidedMaintenanceVehicleBrandAssociation]  # type: ignore[type-var]
):
    """ProvidedMaintenanceVehicleBrandAssociationService для бизнес-логики."""

    repository_type = ProvidedMaintenanceVehicleBrandAssociationRepository

    async def create_provided_maintenance_vehicle_brand_association(
        self, provided_maintenance_vehicle_brand_association: ProvidedMaintenanceVehicleBrandAssociation
    ) -> ProvidedMaintenanceVehicleBrandAssociation:
        """Создание ProvidedMaintenanceVehicleBrandAssociation."""
        if (
            await self.get_one_or_none(
                and_(
                    ProvidedMaintenanceVehicleBrandAssociation.provided_maintenance_id
                    == provided_maintenance_vehicle_brand_association.provided_maintenance_id,
                    ProvidedMaintenanceVehicleBrandAssociation.vehicle_brand_id
                    == provided_maintenance_vehicle_brand_association.vehicle_brand_id,
                )
            )
        ) is not None:
            error_message = "Вы уже привязали данного производителя ТС к этому обслуживанию."
            raise ProvidedMaintenanceVehicleBrandAssociationAlreadyExistsError(error_message)
        logger.info(
            f"Saving "
            f"ProvidedMaintenanceVehicleBrandAssociation{provided_maintenance_vehicle_brand_association.to_dict()} "
            f"in db"
        )
        return await self.create(data=provided_maintenance_vehicle_brand_association)


async def provide_provided_maintenance_vehicle_brand_association_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProvidedMaintenanceVehicleBrandAssociationService]:
    """Возвращает ProvidedMaintenanceVehicleBrandAssociationService."""
    async with ProvidedMaintenanceVehicleBrandAssociationService.new(session=db_session) as service:
        yield service


class ProvidedMaintenanceCountryAssociationRepository(
    SQLAlchemyAsyncRepository[ProvidedMaintenanceCountryAssociation]  # type: ignore[type-var]
):
    """ProvidedMaintenanceCountryAssociationRepository для взаимодействия с БД."""

    id_attribute = "provided_maintenance_id"
    model_type = ProvidedMaintenanceCountryAssociation


class ProvidedMaintenanceCountryAssociationService(
    SQLAlchemyAsyncRepositoryService[ProvidedMaintenanceCountryAssociation]  # type: ignore[type-var]
):
    """ProvidedMaintenanceCountryAssociationService для бизнес-логики."""

    repository_type = ProvidedMaintenanceCountryAssociationRepository

    async def get_provided_maintenance_country_association_by_provided_maintenance_id_and_country_id(
        self, provided_maintenance_id: UUID, country_id: int
    ) -> ProvidedMaintenanceCountryAssociation | None:
        """Получение ProvidedMaintenanceCountryAssociation по provided_maintenance_id и country_id."""
        if (
            provided_maintenance_country_association := await self.get_one_or_none(
                and_(
                    ProvidedMaintenanceCountryAssociation.provided_maintenance_id == provided_maintenance_id,
                    ProvidedMaintenanceCountryAssociation.country_id == country_id,
                )
            )
        ) is None:
            logger.warn(
                f"ProvidedMaintenanceCountryAssociation with {provided_maintenance_id=} "
                f"and {country_id=} doesn't exists in db"
            )
            error_message = "Данное обслуживание не связано с этой страной."
            raise ProvidedMaintenanceCountryAssociationNotFoundError(error_message)
        logger.info(
            f"Got ProvidedMaintenanceCountryAssociation{provided_maintenance_country_association.to_dict()} from db"
        )
        return provided_maintenance_country_association

    async def create_provided_maintenance_country_association(
        self, provided_maintenance_country_association: ProvidedMaintenanceCountryAssociation
    ) -> ProvidedMaintenanceCountryAssociation:
        """Создание ProvidedMaintenanceCountryAssociation."""
        if (
            await self.get_one_or_none(
                and_(
                    ProvidedMaintenanceCountryAssociation.provided_maintenance_id
                    == provided_maintenance_country_association.provided_maintenance_id,
                    ProvidedMaintenanceCountryAssociation.country_id
                    == provided_maintenance_country_association.country_id,
                )
            )
        ) is not None:
            error_message = "Вы уже привязали данную страну к этому обслуживанию."
            raise ProvidedMaintenanceCountryAssociationAlreadyExistsError(error_message)
        logger.info(
            f"Saving ProvidedMaintenanceCountryAssociation{provided_maintenance_country_association.to_dict()} in db"
        )
        return await self.create(data=provided_maintenance_country_association)


async def provide_provided_maintenance_country_association_service(
    db_session: AsyncSession,
) -> AsyncGenerator[ProvidedMaintenanceCountryAssociationService]:
    """Возвращает ProvidedMaintenanceCountryAssociationService."""
    async with ProvidedMaintenanceCountryAssociationService.new(session=db_session) as service:
        yield service


class ProvidedMaintenanceService:
    """ProvidedMaintenanceService для бизнес-логики."""

    def __init__(  # noqa: PLR0913 #TODO(https://gitlab.com/pochini.online/backend/products/-/issues/1): Рефакторинг (вынесение связанных сервисов в отдельный класс)
        self,
        provided_maintenance_type_service: ProvidedMaintenanceTypeService,
        base_provided_maintenance_service: BaseProvidedMaintenanceService,
        provided_maintenance_vehicle_brand_association_service: ProvidedMaintenanceVehicleBrandAssociationService,
        provided_maintenance_country_association_service: ProvidedMaintenanceCountryAssociationService,
        vehicle_brand_service: VehicleBrandService,
        country_service: CountryService,
        mechanic_service: MechanicService,
        autoservice_service: AutoserviceService,
    ) -> None:
        self.provided_maintenance_type_service = provided_maintenance_type_service
        self.base_provided_maintenance_service = base_provided_maintenance_service
        self.provided_maintenance_vehicle_brand_association_service = (
            provided_maintenance_vehicle_brand_association_service
        )
        self.provided_maintenance_country_association_service = provided_maintenance_country_association_service
        self.vehicle_brand_service = vehicle_brand_service
        self.country_service = country_service
        self.mechanic_service = mechanic_service
        self.autoservice_service = autoservice_service

    async def _get_provided_maintenance_with_owner(
        self, provided_maintenance_id: UUID, user: User
    ) -> ProvidedMaintenance:
        provided_maintenance = (
            await self.base_provided_maintenance_service.get_provided_maintenance_by_provided_maintenance_id(
                provided_maintenance_id=provided_maintenance_id
            )
        )
        if provided_maintenance.mechanic_id is not None:
            mechanic = await self.mechanic_service.get_mechanic_by_mechanic_id(
                mechanic_id=provided_maintenance.mechanic_id
            )
            if mechanic.uid != user.uid:
                error_message = "Вы не можете управлять предоставляемыми обслуживаниями другого механика."
                raise MechanicBelongsToAnotherUserError(error_message)
            provided_maintenance.mechanic = mechanic
        if provided_maintenance.autoservice_id is not None:
            autoservice = await self.autoservice_service.get_autoservice_by_autoservice_id(
                autoservice_id=provided_maintenance.autoservice_id
            )
            await self.autoservice_service.validate_autoservice_manage_provided_maintenance_permissions(
                autoservice=autoservice, user=user
            )
            provided_maintenance.autoservice = autoservice
        return provided_maintenance

    async def create_provided_maintenance(
        self, provided_maintenance: ProvidedMaintenance, user: User
    ) -> ProvidedMaintenance:
        """Создание ProvidedMaintenance."""
        provided_maintenance_type = (
            await self.provided_maintenance_type_service.get_provided_maintenance_type_by_provided_maintenance_id(
                provided_maintenance_type_id=provided_maintenance.provided_maintenance_type_id
            )
        )
        mechanic: Mechanic | None = None
        autoservice: Autoservice | None = None
        if provided_maintenance.mechanic_id is not None:
            mechanic = await self.mechanic_service.get_mechanic_by_mechanic_id(
                mechanic_id=provided_maintenance.mechanic_id
            )
            self.mechanic_service.validate_mechanic_owner(mechanic=mechanic, user=user)
        if provided_maintenance.autoservice_id is not None:
            autoservice = await self.autoservice_service.get_autoservice_by_autoservice_id(
                autoservice_id=provided_maintenance.autoservice_id
            )
            await self.autoservice_service.validate_autoservice_manage_provided_maintenance_permissions(
                autoservice=autoservice, user=user
            )
        logger.info(f"Saving ProvidedMaintenance{provided_maintenance.to_dict()} in db")
        provided_maintenance = await self.base_provided_maintenance_service.create(data=provided_maintenance)
        (
            provided_maintenance.provided_maintenance_type,
            provided_maintenance.mechanic,
            provided_maintenance.autoservice,
        ) = provided_maintenance_type, mechanic, autoservice
        return provided_maintenance

    async def create_provided_maintenance_country_association(
        self, provided_maintenance_country_association: ProvidedMaintenanceCountryAssociation, user: User
    ) -> ProvidedMaintenanceCountryAssociation:
        """Создание связи между ProvidedMaintenance и Country."""
        await self._get_provided_maintenance_with_owner(
            provided_maintenance_id=provided_maintenance_country_association.provided_maintenance_id, user=user
        )
        await self.country_service.get_country_by_country_id(
            country_id=provided_maintenance_country_association.country_id
        )
        return (
            await self.provided_maintenance_country_association_service.create_provided_maintenance_country_association(
                provided_maintenance_country_association=provided_maintenance_country_association
            )
        )

    async def create_provided_maintenance_vehicle_brand_association(
        self, provided_maintenance_vehicle_brand_association: ProvidedMaintenanceVehicleBrandAssociation, user: User
    ) -> ProvidedMaintenanceVehicleBrandAssociation:
        """Создание связи между ProvidedMaintenance и VehicleBrand."""
        await self._get_provided_maintenance_with_owner(
            provided_maintenance_id=provided_maintenance_vehicle_brand_association.provided_maintenance_id, user=user
        )
        await self.vehicle_brand_service.get_vehicle_brand_by_vehicle_brand_id(
            vehicle_brand_id=provided_maintenance_vehicle_brand_association.vehicle_brand_id
        )
        return await self.provided_maintenance_vehicle_brand_association_service.create_provided_maintenance_vehicle_brand_association(  # noqa: E501
            provided_maintenance_vehicle_brand_association=provided_maintenance_vehicle_brand_association
        )


async def provide_provided_maintenance_service(  # noqa: PLR0913 #TODO(https://gitlab.com/pochini.online/backend/products/-/issues/1): Рефакторинг (вынесение связанных сервисов в отдельный класс)
    provided_maintenance_type_service: ProvidedMaintenanceTypeService,
    base_provided_maintenance_service: BaseProvidedMaintenanceService,
    provided_maintenance_vehicle_brand_association_service: ProvidedMaintenanceVehicleBrandAssociationService,
    provided_maintenance_country_association_service: ProvidedMaintenanceCountryAssociationService,
    vehicle_brand_service: VehicleBrandService,
    country_service: CountryService,
    mechanic_service: MechanicService,
    autoservice_service: AutoserviceService,
) -> ProvidedMaintenanceService:
    """Возвращает ProvidedMaintenanceService."""
    return ProvidedMaintenanceService(
        provided_maintenance_type_service=provided_maintenance_type_service,
        base_provided_maintenance_service=base_provided_maintenance_service,
        provided_maintenance_vehicle_brand_association_service=provided_maintenance_vehicle_brand_association_service,
        provided_maintenance_country_association_service=provided_maintenance_country_association_service,
        vehicle_brand_service=vehicle_brand_service,
        country_service=country_service,
        mechanic_service=mechanic_service,
        autoservice_service=autoservice_service,
    )
