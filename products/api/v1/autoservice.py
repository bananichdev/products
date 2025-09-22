"""Модуль с ручками сущности Autoservice."""

from typing import Annotated, Any
from uuid import UUID

from litestar import Controller, Request, Response, get, patch, post
from litestar.datastructures import Cookie
from litestar.exceptions import NotFoundException, PermissionDeniedException
from litestar.params import Parameter
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from products.exceptions.autoservice import (
    AutoserviceNotFoundError,
    AutoserviceUserDoesntHavePermissionsError,
    AutoserviceUserNotFoundError,
)
from products.models.autoservice import Autoservice, AutoservicePatchDTO, AutoservicePostDTO, AutoserviceSimpleReturnDTO
from products.models.user import User
from products.services.autoservice import AutoserviceService


class AutoserviceController(Controller):
    """Ручки для работы с сущностью Autoservice."""

    tags = ["Autoservice"]
    path = "/autoservices"

    return_dto = AutoserviceSimpleReturnDTO

    @get("/{autoservice_id:uuid}", status_code=HTTP_200_OK, exclude_from_user_auth=True)
    async def get_autoservice_by_autoservice_id(
        self,
        autoservice_id: Annotated[UUID, Parameter(description="Уникальный идентификатор автосервиса.")],
        autoservice_service: AutoserviceService,
    ) -> Autoservice:
        """Получение автосервиса по autoservice_id."""
        try:
            return await autoservice_service.get_autoservice_by_autoservice_id(autoservice_id=autoservice_id)
        except AutoserviceNotFoundError as e:
            raise NotFoundException(str(e)) from e

    @post(
        "/",
        dto=AutoservicePostDTO,
        status_code=HTTP_201_CREATED,
    )
    async def create_autoservice(
        self, request: Request[User, Token, Any], data: Autoservice, autoservice_service: AutoserviceService
    ) -> Response[Autoservice]:
        """Создание нового клиента."""
        autoservice = await autoservice_service.create_autoservice(autoservice=data, user=request.user)
        response = Response(autoservice, cookies=request.cookies)
        response.set_cookie(Cookie(key="autoservice_id", value=str(autoservice.autoservice_id)))
        response.delete_cookie(key="customer_id")
        response.delete_cookie(key="mechanic_id")
        return response

    @patch(
        "/{autoservice_id:uuid}",
        dto=AutoservicePatchDTO,
        status_code=HTTP_200_OK,
    )
    async def patch_autoservice(
        self,
        request: Request[User, Token, Any],
        autoservice_id: UUID,
        data: Autoservice,
        autoservice_service: AutoserviceService,
    ) -> Autoservice:
        """Частичное обновление клиента."""
        try:
            return await autoservice_service.patch_autoservice(
                autoservice_id=autoservice_id, changed_autoservice=data, user=request.user
            )
        except AutoserviceNotFoundError as e:
            raise NotFoundException(str(e)) from e
        except (AutoserviceUserNotFoundError, AutoserviceUserDoesntHavePermissionsError) as e:
            raise PermissionDeniedException(str(e)) from e
