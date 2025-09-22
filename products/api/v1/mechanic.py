"""Модуль с ручками сущности Mechanic."""

from typing import Annotated, Any
from uuid import UUID

from litestar import Controller, Request, Response, get, patch, post
from litestar.datastructures import Cookie
from litestar.exceptions import NotFoundException, PermissionDeniedException
from litestar.params import Parameter
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from products.exceptions.mechanic import MechanicBelongsToAnotherUserError, MechanicNotFoundError
from products.models.mechanic import Mechanic, MechanicPatchDTO, MechanicPostDTO, MechanicSimpleReturnDTO
from products.models.user import User
from products.services.mechanic import MechanicService


class MechanicController(Controller):
    """Ручки для работы с сущностью Mechanic."""

    tags = ["Mechanic"]
    path = "/mechanics"

    return_dto = MechanicSimpleReturnDTO

    @get("/{mechanic_id:uuid}", status_code=HTTP_200_OK, exclude_from_user_auth=True)
    async def get_mechanic_by_mechanic_id(
        self,
        mechanic_id: Annotated[UUID, Parameter(description="Уникальный идентификатор механика")],
        mechanic_service: MechanicService,
    ) -> Mechanic:
        """Получение клиента по customer_id."""
        try:
            return await mechanic_service.get_mechanic_by_mechanic_id(mechanic_id=mechanic_id)
        except MechanicNotFoundError as e:
            raise NotFoundException(str(e)) from e

    @post(
        "/",
        dto=MechanicPostDTO,
        status_code=HTTP_201_CREATED,
    )
    async def create_mechanic(
        self, request: Request[User, Token, Any], data: Mechanic, mechanic_service: MechanicService
    ) -> Response[Mechanic]:
        """Создание нового клиента."""
        mechanic = await mechanic_service.create_mechanic(mechanic=data, user=request.user)
        response = Response(mechanic, cookies=request.cookies)
        response.set_cookie(Cookie(key="mechanic_id", value=str(mechanic.mechanic_id)))
        response.delete_cookie(key="customer_id")
        response.delete_cookie(key="autoservice_id")
        return response

    @patch("/{mechanic_id:uuid}", dto=MechanicPatchDTO, status_code=HTTP_200_OK)
    async def patch_mechanic(
        self, request: Request[User, Token, Any], mechanic_id: UUID, data: Mechanic, mechanic_service: MechanicService
    ) -> Mechanic:
        """Частичное обновление клиента."""
        try:
            return await mechanic_service.patch_mechanic(
                mechanic_id=mechanic_id, changed_mechanic=data, user=request.user
            )
        except MechanicNotFoundError as e:
            raise NotFoundException(str(e)) from e
        except MechanicBelongsToAnotherUserError as e:
            raise PermissionDeniedException(str(e)) from e
