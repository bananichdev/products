"""Пакет с моделями."""

from products.models.autoservice import Autoservice, AutoserviceUser, AutoserviceUserPermissions
from products.models.country import Country
from products.models.maintenance import (
    ProvidedMaintenance,
    ProvidedMaintenanceCategory,
    ProvidedMaintenanceCountryAssociation,
    ProvidedMaintenanceType,
    ProvidedMaintenanceVehicleBrandAssociation,
)
from products.models.mechanic import Mechanic
from products.models.user import User
from products.models.vehicle import Vehicle, VehicleBrand, VehicleGeneration, VehicleModel

__all__ = [
    "Autoservice",
    "AutoserviceUser",
    "AutoserviceUserPermissions",
    "Country",
    "Mechanic",
    "ProvidedMaintenance",
    "ProvidedMaintenanceCategory",
    "ProvidedMaintenanceCountryAssociation",
    "ProvidedMaintenanceType",
    "ProvidedMaintenanceVehicleBrandAssociation",
    "User",
    "Vehicle",
    "VehicleBrand",
    "VehicleGeneration",
    "VehicleModel",
]
