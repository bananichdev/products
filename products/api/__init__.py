"""Пакет с API Router."""

from litestar import Router


def provide_api_router(v1_router: Router) -> Router:
    """Возвращает API роутер."""
    return Router(path="/api", route_handlers=[v1_router])
