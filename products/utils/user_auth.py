"""Модуль с утилитами для JWT."""

from uuid import UUID

from litestar.connection import ASGIConnection
from litestar.security.jwt import JWTCookieAuth, Token
from litestar_utils.middlewares.auth import JWTCookieLoggedAuthenticationMiddleware

from products.models.user import User
from products.settings import AuthSettings


async def retrieve_user_handler(token: Token, _: ASGIConnection) -> User | None:
    """Получение User."""
    if not token.sub:
        return None
    return User(uid=UUID(token.sub))


async def revoked_token_handler(token: Token, connection: ASGIConnection) -> bool:
    """Проверка отозванного токена."""
    if token.jti is None:
        return True
    # TODO(@vzlombn): добавить проверку токена в БД user-id(хождение в сервис через HTTP)  # noqa: TD003
    blacklist_store = connection.app.stores.get("blacklist_store")
    return (await blacklist_store.get(token.jti)) is not None


def provide_user_auth(auth_settings: AuthSettings) -> JWTCookieAuth[User, Token]:
    """Возвращает JWTCookieAuth."""
    return JWTCookieAuth[User, Token](
        retrieve_user_handler=retrieve_user_handler,
        revoked_token_handler=revoked_token_handler,
        algorithm=auth_settings.jwt_algorithm,
        exclude=["/schema"],
        exclude_opt_key="exclude_from_user_auth",
        token_secret=auth_settings.jwt_secret.get_secret_value(),
        auth_header=auth_settings.jwt_token_header_key,
        key=auth_settings.jwt_token_cookie_key,
        authentication_middleware_class=JWTCookieLoggedAuthenticationMiddleware,
    )
