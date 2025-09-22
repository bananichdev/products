"""Модуль с подготовкой приложения."""

from litestar import Litestar
from litestar.di import Provide
from litestar_granian import GranianPlugin
from litestar_utils.middlewares.trace_id import TraceIDMiddleware
from litestar_utils.plugins.middlewares_sorter import MiddlewaresSorterPlugin

from products.api import provide_api_router
from products.api.v1 import provide_v1_router
from products.services.autoservice import (
    provide_autoservice_service,
    provide_autoservice_user_service,
    provide_base_autoservice_service,
)
from products.services.country import provide_country_service
from products.services.customer import provide_customer_service
from products.services.maintenance import (
    provide_base_provided_maintenance_service,
    provide_provided_maintenance_category_service,
    provide_provided_maintenance_country_association_service,
    provide_provided_maintenance_service,
    provide_provided_maintenance_type_service,
    provide_provided_maintenance_vehicle_brand_association_service,
)
from products.services.mechanic import provide_mechanic_service
from products.services.vehicle import (
    provide_base_vehicle_service,
    provide_common_vehicle_service,
    provide_vehicle_brand_service,
    provide_vehicle_generation_service,
    provide_vehicle_model_service,
    provide_vehicle_service,
)
from products.settings import (
    provide_app_settings,
    provide_auth_settings,
    provide_blacklist_store,
    provide_database_settings,
    provide_logging_settings,
    provide_openapi_config,
    provide_redis_settings,
    provide_redis_store,
    provide_sqlalchemy_init_plugin,
    provide_structlog_plugin,
)
from products.utils.user_auth import provide_user_auth


def provide_app() -> Litestar:
    """Возвращает Litestar app."""
    # App
    app_settings = provide_app_settings()

    # Server
    openapi_config = provide_openapi_config(app_settings)

    # Controllers
    v1_router = provide_v1_router()
    api_router = provide_api_router(v1_router)

    # Redis
    redis_settings = provide_redis_settings()
    redis_store = provide_redis_store(redis_settings)
    blacklist_store = provide_blacklist_store(redis_store)

    # SQLAlchemy
    database_settings = provide_database_settings()
    sqlalchemy_init_plugin = provide_sqlalchemy_init_plugin(database_settings)

    # Auth
    auth_settings = provide_auth_settings()
    user_auth = provide_user_auth(auth_settings)

    # Structlog
    logging_settings = provide_logging_settings()
    structlog_plugin = provide_structlog_plugin(logging_settings=logging_settings, auth_settings=auth_settings)

    return Litestar(
        path=app_settings.app_name,
        debug=app_settings.env == "local",
        openapi_config=None if app_settings.env == "prod" else openapi_config,
        stores={"blacklist_store": blacklist_store},
        dependencies={
            "country_service": Provide(provide_country_service),
            "blacklist_store": Provide(provide_blacklist_store, use_cache=True, sync_to_thread=False),
            "customer_service": Provide(provide_customer_service),
            "vehicle_brand_service": Provide(provide_vehicle_brand_service),
            "vehicle_model_service": Provide(provide_vehicle_model_service),
            "vehicle_generation_service": Provide(provide_vehicle_generation_service),
            "common_vehicle_service": Provide(provide_common_vehicle_service),
            "base_vehicle_service": Provide(provide_base_vehicle_service),
            "vehicle_service": Provide(provide_vehicle_service),
            "redis_settings": Provide(provide_redis_settings, use_cache=True, sync_to_thread=False),
            "redis_store": Provide(provide_redis_store, use_cache=True, sync_to_thread=False),
            "base_autoservice_service": Provide(provide_base_autoservice_service),
            "autoservice_user_service": Provide(provide_autoservice_user_service),
            "autoservice_service": Provide(provide_autoservice_service),
            "mechanic_service": Provide(provide_mechanic_service),
            "provided_maintenance_category_service": Provide(provide_provided_maintenance_category_service),
            "provided_maintenance_type_service": Provide(provide_provided_maintenance_type_service),
            "base_provided_maintenance_service": Provide(provide_base_provided_maintenance_service),
            "provided_maintenance_vehicle_brand_association_service": Provide(
                provide_provided_maintenance_vehicle_brand_association_service
            ),
            "provided_maintenance_country_association_service": Provide(
                provide_provided_maintenance_country_association_service
            ),
            "provided_maintenance_service": Provide(provide_provided_maintenance_service),
        },
        route_handlers=[api_router],
        on_app_init=[user_auth.on_app_init],
        plugins=[structlog_plugin, sqlalchemy_init_plugin, GranianPlugin(), MiddlewaresSorterPlugin()],
        middleware=[TraceIDMiddleware],
    )
