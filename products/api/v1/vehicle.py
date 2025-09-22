"""Модуль с ручками сущности Vehicle."""

from typing import Annotated
from uuid import UUID

from litestar import Controller, get, post
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from products.exceptions.customer import CustomerNotFoundError
from products.exceptions.http import ConflictException
from products.exceptions.vehicle import (
    VehicleBrandNotFoundError,
    VehicleGenerationDoesntMatchWithVehicleModelError,
    VehicleGenerationNotFoundError,
    VehicleModelDoesntMatchWithVehicleBrandError,
    VehicleModelNotFoundError,
    VehicleNotFoundError,
)
from products.models.vehicle import Vehicle, VehiclePostDTO, VehicleSimpleReturnDTO
from products.services.vehicle import VehicleService


class VehicleController(Controller):
    """Ручки для работы с сущностью Vehicle."""

    tags = ["Vehicle"]
    path = "/vehicle"

    return_dto = VehicleSimpleReturnDTO

    @get("/{vehicle_id:uuid}", status_code=HTTP_200_OK, exclude_from_user_auth=True)
    async def get_vehicle_by_vehicle_id(
        self,
        vehicle_id: Annotated[UUID, Parameter(description="Уникальный идентификатор автомобиля")],
        vehicle_service: VehicleService,
    ) -> Vehicle:
        """Получение Vehicle по vehicle_id."""
        try:
            return await vehicle_service.get_vehicle_by_vehicle_id(vehicle_id=vehicle_id)
        except VehicleNotFoundError as e:
            raise NotFoundException(str(e)) from e

    @post(
        "/",
        dto=VehiclePostDTO,
        status_code=HTTP_201_CREATED,
    )
    async def create_vehicle(self, data: Vehicle, vehicle_service: VehicleService) -> Vehicle:
        """Создание нового клиента."""
        try:
            return await vehicle_service.create_vehicle(vehicle=data)
        except (
            CustomerNotFoundError,
            VehicleBrandNotFoundError,
            VehicleModelNotFoundError,
            VehicleGenerationNotFoundError,
            VehicleModelDoesntMatchWithVehicleBrandError,
            VehicleGenerationDoesntMatchWithVehicleModelError,
        ) as e:
            raise ConflictException(str(e)) from e
