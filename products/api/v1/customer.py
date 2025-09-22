"""Модуль с ручками сущности Customer."""

from typing import Annotated, Any
from uuid import UUID

from litestar import Controller, Request, Response, get, patch, post
from litestar.datastructures import Cookie
from litestar.exceptions import NotFoundException, PermissionDeniedException
from litestar.params import Parameter
from litestar.security.jwt import Token
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED

from products.exceptions.customer import CustomerBelongsToAnotherUserError, CustomerNotFoundError
from products.models.customer import Customer, CustomerPatchDTO, CustomerPostDTO, CustomerSimpleReturnDTO
from products.models.user import User
from products.services.customer import CustomerService


class CustomerController(Controller):
    """Ручки для работы с сущностью Customer."""

    tags = ["Customer"]
    path = "/customers"

    return_dto = CustomerSimpleReturnDTO

    @get("/{customer_id:uuid}", status_code=HTTP_200_OK, exclude_from_user_auth=True)
    async def get_customer_by_customer_id(
        self,
        customer_id: Annotated[UUID, Parameter(description="Уникальный идентификатор клиента")],
        customer_service: CustomerService,
    ) -> Customer:
        """Получение клиента по customer_id."""
        try:
            return await customer_service.get_customer_by_customer_id(customer_id=customer_id)
        except CustomerNotFoundError as e:
            raise NotFoundException(str(e)) from e

    @post(
        "/",
        dto=CustomerPostDTO,
        status_code=HTTP_201_CREATED,
    )
    async def create_customer(
        self, request: Request[User, Token, Any], data: Customer, customer_service: CustomerService
    ) -> Response[Customer]:
        """Создание нового клиента."""
        customer = await customer_service.create_customer(customer=data, user=request.user)
        response = Response(customer, cookies=request.cookies)
        response.set_cookie(Cookie(key="customer_id", value=str(customer.customer_id)))
        response.delete_cookie(key="mechanic_id")
        response.delete_cookie(key="autoservice_id")
        return response

    @patch("/{customer_id:uuid}", dto=CustomerPatchDTO, status_code=HTTP_200_OK)
    async def patch_customer(
        self, request: Request[User, Token, Any], customer_id: UUID, data: Customer, customer_service: CustomerService
    ) -> Customer:
        """Частичное обновление клиента."""
        try:
            return await customer_service.patch_customer(
                customer_id=customer_id, changed_customer=data, user=request.user
            )
        except CustomerNotFoundError as e:
            raise NotFoundException(str(e)) from e
        except CustomerBelongsToAnotherUserError as e:
            raise PermissionDeniedException(str(e)) from e
