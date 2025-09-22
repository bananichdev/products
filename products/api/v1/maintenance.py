"""Модуль с ручками сущности Maintenance."""

from typing import Any

from litestar import Controller, Request, post
from litestar.exceptions import NotFoundException, PermissionDeniedException

from products.exceptions.autoservice import (
    AutoserviceNotFoundError,
    AutoserviceUserDoesntHavePermissionsError,
    AutoserviceUserNotFoundError,
)
from products.exceptions.country import CountryNotFoundError
from products.exceptions.http import ConflictException
from products.exceptions.maintenance import (
    ProvidedMaintenanceCountryAssociationAlreadyExistsError,
    ProvidedMaintenanceNotFoundError,
    ProvidedMaintenanceTypeNotFoundError,
    ProvidedMaintenanceVehicleBrandAssociationAlreadyExistsError,
)
from products.exceptions.mechanic import MechanicBelongsToAnotherUserError, MechanicNotFoundError
from products.exceptions.vehicle import VehicleBrandNotFoundError
from products.models.maintenance import (
    ProvidedMaintenance,
    ProvidedMaintenanceCountryAssociation,
    ProvidedMaintenanceCountryAssociationPostDTO,
    ProvidedMaintenanceCountryAssociationReturnDTO,
    ProvidedMaintenancePostDTO,
    ProvidedMaintenanceReturnDTO,
    ProvidedMaintenanceVehicleBrandAssociation,
    ProvidedMaintenanceVehicleBrandAssociationPostDTO,
    ProvidedMaintenanceVehicleBrandAssociationReturnDTO,
)
from products.models.user import User
from products.services.maintenance import ProvidedMaintenanceService


class MaintenanceController(Controller):
    """Ручки для работы с сущностью Maintenance."""

    tags = ["Maintenance"]
    path = "/maintenance"

    @post("/provided_maintenance", dto=ProvidedMaintenancePostDTO, return_dto=ProvidedMaintenanceReturnDTO)
    async def create_provided_maintenance(
        self,
        data: ProvidedMaintenance,
        provided_maintenance_service: ProvidedMaintenanceService,
        request: Request[User, Any, Any],
    ) -> ProvidedMaintenance:
        """Создание ProvidedMaintenanceService."""
        try:
            return await provided_maintenance_service.create_provided_maintenance(
                provided_maintenance=data, user=request.user
            )
        except (ProvidedMaintenanceTypeNotFoundError, MechanicNotFoundError, AutoserviceNotFoundError) as e:
            raise NotFoundException(str(e)) from e
        except (
            MechanicBelongsToAnotherUserError,
            AutoserviceUserNotFoundError,
            AutoserviceUserDoesntHavePermissionsError,
        ) as e:
            raise PermissionDeniedException(str(e)) from e

    @post(
        "/provided_maintenance/countries",
        dto=ProvidedMaintenanceCountryAssociationPostDTO,
        return_dto=ProvidedMaintenanceCountryAssociationReturnDTO,
    )
    async def create_provided_maintenance_country_association(
        self,
        data: ProvidedMaintenanceCountryAssociation,
        provided_maintenance_service: ProvidedMaintenanceService,
        request: Request[User, Any, Any],
    ) -> ProvidedMaintenanceCountryAssociation:
        """Создание ProvidedMaintenanceService."""
        try:
            return await provided_maintenance_service.create_provided_maintenance_country_association(
                provided_maintenance_country_association=data, user=request.user
            )
        except (ProvidedMaintenanceNotFoundError, CountryNotFoundError) as e:
            raise NotFoundException(str(e)) from e
        except (
            MechanicBelongsToAnotherUserError,
            AutoserviceUserNotFoundError,
            AutoserviceUserDoesntHavePermissionsError,
        ) as e:
            raise PermissionDeniedException(str(e)) from e
        except ProvidedMaintenanceCountryAssociationAlreadyExistsError as e:
            raise ConflictException(str(e)) from e

    @post(
        "/provided_maintenance/vehicle_brands",
        dto=ProvidedMaintenanceVehicleBrandAssociationPostDTO,
        return_dto=ProvidedMaintenanceVehicleBrandAssociationReturnDTO,
    )
    async def create_provided_maintenance_vehicle_brand_association(
        self,
        data: ProvidedMaintenanceVehicleBrandAssociation,
        provided_maintenance_service: ProvidedMaintenanceService,
        request: Request[User, Any, Any],
    ) -> ProvidedMaintenanceVehicleBrandAssociation:
        """Создание ProvidedMaintenanceService."""
        try:
            return await provided_maintenance_service.create_provided_maintenance_vehicle_brand_association(
                provided_maintenance_vehicle_brand_association=data, user=request.user
            )
        except (ProvidedMaintenanceNotFoundError, VehicleBrandNotFoundError) as e:
            raise NotFoundException(str(e)) from e
        except (
            MechanicBelongsToAnotherUserError,
            AutoserviceUserNotFoundError,
            AutoserviceUserDoesntHavePermissionsError,
        ) as e:
            raise PermissionDeniedException(str(e)) from e
        except ProvidedMaintenanceVehicleBrandAssociationAlreadyExistsError as e:
            raise ConflictException(str(e)) from e
