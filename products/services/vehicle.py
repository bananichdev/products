"""Модуль с VehicleService."""

from collections.abc import AsyncGenerator
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.vehicle import (
    VehicleBrandNotFoundError,
    VehicleGenerationDoesntMatchWithVehicleModelError,
    VehicleGenerationNotFoundError,
    VehicleModelDoesntMatchWithVehicleBrandError,
    VehicleModelNotFoundError,
    VehicleNotFoundError,
)
from products.models.vehicle import Vehicle, VehicleBrand, VehicleGeneration, VehicleModel
from products.services.customer import CustomerService
from products.settings import logger


class VehicleBrandRepository(SQLAlchemyAsyncRepository[VehicleBrand]):  # type: ignore[type-var]
    """VehicleBrandRepository для взаимодействия с БД."""

    id_attribute = "vehicle_brand_id"
    model_type = VehicleBrand


class VehicleBrandService(SQLAlchemyAsyncRepositoryService[VehicleBrand]):  # type: ignore[type-var]
    """VehicleBrandService для бизнес-логики."""

    repository_type = VehicleBrandRepository

    async def get_vehicle_brand_by_vehicle_brand_id(self, vehicle_brand_id: int) -> VehicleBrand:
        """Получение VehicleBrand по vehicle_brand_id."""
        if (vehicle_brand := await self.get_one_or_none(VehicleBrand.vehicle_brand_id == vehicle_brand_id)) is None:
            logger.warn(f"VehicleBrand with vehicle_brand_id={vehicle_brand_id} doesn't exist in db")
            error_message = "Такой марки ТС не существует."
            raise VehicleBrandNotFoundError(error_message)
        logger.info(f"Got VehicleBrand{vehicle_brand.to_dict()} from db")
        return vehicle_brand


async def provide_vehicle_brand_service(db_session: AsyncSession) -> AsyncGenerator[VehicleBrandService]:
    """Возвращает VehicleBrandService."""
    async with VehicleBrandService.new(session=db_session) as service:
        yield service


class VehicleModelRepository(SQLAlchemyAsyncRepository[VehicleModel]):  # type: ignore[type-var]
    """VehicleModelRepository для взаимодействия с БД."""

    id_attribute = "vehicle_model_id"
    model_type = VehicleModel


class VehicleModelService(SQLAlchemyAsyncRepositoryService[VehicleModel]):  # type: ignore[type-var]
    """VehicleModelService для бизнес-логики."""

    repository_type = VehicleModelRepository

    async def get_vehicle_model_by_vehicle_model_id(self, vehicle_model_id: int) -> VehicleModel:
        """Получение VehicleModel по vehicle_model_id."""
        if (vehicle_model := await self.get_one_or_none(VehicleModel.vehicle_model_id == vehicle_model_id)) is None:
            logger.warn(f"VehicleModel with vehicle_model_id={vehicle_model_id} doesn't exist in db")
            error_message = "Такой модели ТС не существует."
            raise VehicleModelNotFoundError(error_message)
        logger.info(f"Got VehicleModel{vehicle_model.to_dict()} from db")
        return vehicle_model


async def provide_vehicle_model_service(db_session: AsyncSession) -> AsyncGenerator[VehicleModelService]:
    """Возвращает VehicleModelService."""
    async with VehicleModelService.new(session=db_session) as service:
        yield service


class VehicleGenerationRepository(SQLAlchemyAsyncRepository[VehicleGeneration]):  # type: ignore[type-var]
    """VehicleGenerationRepository для взаимодействия с БД."""

    id_attribute = "vehicle_generation_id"
    model_type = VehicleGeneration


class VehicleGenerationService(SQLAlchemyAsyncRepositoryService[VehicleGeneration]):  # type: ignore[type-var]
    """VehicleGenerationService для бизнес-логики."""

    repository_type = VehicleGenerationRepository

    async def get_vehicle_generation_by_vehicle_generation_id(self, vehicle_generation_id: int) -> VehicleGeneration:
        """Получение VehicleGeneration по vehicle_generation_id."""
        if (
            vehicle_generation := await self.get_one_or_none(
                VehicleGeneration.vehicle_generation_id == vehicle_generation_id
            )
        ) is None:
            logger.warn(f"VehicleGeneration with vehicle_generation_id={vehicle_generation_id} doesn't exist in db")
            error_message = "Такого поколения ТС не существует."
            raise VehicleGenerationNotFoundError(error_message)
        logger.info(f"Got VehicleModel{vehicle_generation.to_dict()} from db")
        return vehicle_generation


async def provide_vehicle_generation_service(db_session: AsyncSession) -> AsyncGenerator[VehicleGenerationService]:
    """Возвращает VehicleGenerationService."""
    async with VehicleGenerationService.new(session=db_session) as service:
        yield service


class CommonVehicleService:
    """Сервис для валидации общих параметров для всех ТС."""

    def __init__(
        self,
        vehicle_brand_service: VehicleBrandService,
        vehicle_model_service: VehicleModelService,
        vehicle_generation_service: VehicleGenerationService,
    ) -> None:
        self.vehicle_brand_service = vehicle_brand_service
        self.vehicle_model_service = vehicle_model_service
        self.vehicle_generation_service = vehicle_generation_service

    async def validate_vehicle_params(
        self, vehicle_brand_id: int, vehicle_model_id: int, vehicle_generation_id: int
    ) -> tuple[VehicleBrand, VehicleModel, VehicleGeneration]:
        """Валидация общих параметров для всех ТС."""
        vehicle_brand = await self.vehicle_brand_service.get_vehicle_brand_by_vehicle_brand_id(
            vehicle_brand_id=vehicle_brand_id
        )
        vehicle_model = await self.vehicle_model_service.get_vehicle_model_by_vehicle_model_id(
            vehicle_model_id=vehicle_model_id
        )
        if vehicle_model.vehicle_brand_id != vehicle_brand.vehicle_brand_id:
            logger.warn(
                f"VehicleBrand doesn't match VehicleModel, "
                f"because VehicleModel.vehicle_brand_id={vehicle_model.vehicle_brand_id} != "
                f"VehicleBrand.vehicle_brand_id={vehicle_brand.vehicle_brand_id}"
            )
            error_message = "Данная модель ТС не соответствует данной марке ТС."
            raise VehicleModelDoesntMatchWithVehicleBrandError(error_message)
        vehicle_generation = await self.vehicle_generation_service.get_vehicle_generation_by_vehicle_generation_id(
            vehicle_generation_id=vehicle_generation_id
        )
        if vehicle_generation.vehicle_model_id != vehicle_model.vehicle_model_id:
            logger.warn(
                f"VehicleModel doesn't match VehicleGeneration, "
                f"because VehicleGeneration.vehicle_model_id={vehicle_generation.vehicle_model_id} != "
                f"VehicleModel.vehicle_model_id={vehicle_model.vehicle_model_id}"
            )
            error_message = "Данное поколение ТС не соответствует данной модели ТС."
            raise VehicleGenerationDoesntMatchWithVehicleModelError(error_message)
        return vehicle_brand, vehicle_model, vehicle_generation


async def provide_common_vehicle_service(
    vehicle_brand_service: VehicleBrandService,
    vehicle_model_service: VehicleModelService,
    vehicle_generation_service: VehicleGenerationService,
) -> CommonVehicleService:
    """Возвращает CommonVehicleService."""
    return CommonVehicleService(
        vehicle_brand_service=vehicle_brand_service,
        vehicle_model_service=vehicle_model_service,
        vehicle_generation_service=vehicle_generation_service,
    )


class BaseVehicleRepository(SQLAlchemyAsyncRepository[Vehicle]):  # type: ignore[type-var]
    """BaseVehicleRepository для взаимодействия с БД."""

    id_attribute = "vehicle_id"
    model_type = Vehicle


class BaseVehicleService(SQLAlchemyAsyncRepositoryService[Vehicle]):  # type: ignore[type-var]
    """BaseVehicleService для бизнес-логики."""

    repository_type = BaseVehicleRepository

    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Создание сущности Vehicle."""
        vehicle = await self.create(vehicle)
        logger.info(f"Saving Vehicle{vehicle.to_dict()} in db")
        return vehicle


async def provide_base_vehicle_service(db_session: AsyncSession) -> AsyncGenerator[BaseVehicleService]:
    """Возвращает BaseVehicleService."""
    async with BaseVehicleService.new(session=db_session) as service:
        yield service


class VehicleService:
    """VehicleService для бизнес-логики."""

    def __init__(
        self,
        common_vehicle_service: CommonVehicleService,
        base_vehicle_service: BaseVehicleService,
        customer_service: CustomerService,
    ) -> None:
        self.common_vehicle_service = common_vehicle_service
        self.base_vehicle_service = base_vehicle_service
        self.customer_service = customer_service

    async def get_vehicle_by_vehicle_id(self, vehicle_id: UUID) -> Vehicle:
        """Получение Vehicle по vehicle_id."""
        if (
            vehicle := await self.base_vehicle_service.get_one_or_none(
                Vehicle.vehicle_id == vehicle_id,
            )
        ) is None:
            logger.warning(f"Vehicle with {vehicle_id} doesn't exists in db")
            error_message = "ТС не найдено"
            raise VehicleNotFoundError(error_message)
        logger.info(f"Got Vehicle{vehicle.to_dict()} from db")
        return vehicle

    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Создание ТС."""
        logger.info("Creating Vehicle")
        vehicle_brand, vehicle_model, vehicle_generation = await self.common_vehicle_service.validate_vehicle_params(
            vehicle_brand_id=vehicle.vehicle_brand_id,
            vehicle_model_id=vehicle.vehicle_model_id,
            vehicle_generation_id=vehicle.vehicle_generation_id,
        )
        customer = await self.customer_service.get_customer_by_customer_id(customer_id=vehicle.customer_id)
        vehicle = await self.base_vehicle_service.create_vehicle(vehicle=vehicle)
        vehicle.vehicle_brand, vehicle.vehicle_model, vehicle.vehicle_generation, vehicle.customer = (
            vehicle_brand,
            vehicle_model,
            vehicle_generation,
            customer,
        )
        logger.info("Vehicle was created")
        return vehicle


async def provide_vehicle_service(
    common_vehicle_service: CommonVehicleService,
    base_vehicle_service: BaseVehicleService,
    customer_service: CustomerService,
) -> VehicleService:
    """Возвращает VehicleService."""
    return VehicleService(
        common_vehicle_service=common_vehicle_service,
        base_vehicle_service=base_vehicle_service,
        customer_service=customer_service,
    )
