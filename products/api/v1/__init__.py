"""Пакет с инициализацией API Router V1."""

from litestar import Router

from products.api.v1.autoservice import AutoserviceController
from products.api.v1.customer import CustomerController
from products.api.v1.maintenance import MaintenanceController
from products.api.v1.mechanic import MechanicController
from products.api.v1.vehicle import VehicleController


def provide_v1_router() -> Router:
    """Возвращает V1 роутер."""
    return Router(
        path="/v1",
        route_handlers=[
            CustomerController,
            AutoserviceController,
            MechanicController,
            VehicleController,
            MaintenanceController,
        ],
    )
