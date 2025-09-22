"""Модуль с CustomerService."""

from collections.abc import AsyncGenerator
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.customer import CustomerBelongsToAnotherUserError, CustomerNotFoundError
from products.models.customer import Customer
from products.models.user import User
from products.settings import logger


class CustomerRepository(SQLAlchemyAsyncRepository[Customer]):  # type: ignore[type-var]
    """CustomerRepository для взаимодействия с БД."""

    id_attribute = "customer_id"
    model_type = Customer


class CustomerService(SQLAlchemyAsyncRepositoryService[Customer]):  # type: ignore[type-var]
    """CustomerService для бизнес-логики."""

    repository_type = CustomerRepository

    async def get_customer_by_customer_id(self, customer_id: UUID) -> Customer:
        """Получение Customer по customer_id."""
        if (
            customer := await self.get_one_or_none(
                Customer.customer_id == customer_id,
            )
        ) is None:
            logger.warn(f"Customer with {customer_id=} doesn't exists in db")
            error_message = "Клиент не найден."
            raise CustomerNotFoundError(error_message)
        logger.info(f"Got Customer{customer.to_dict()} from db")
        return customer

    async def create_customer(self, customer: Customer, user: User) -> Customer:
        """Создание сущности Customer."""
        if (saved_customer := await self.get_one_or_none(Customer.uid == user.uid)) is not None:
            logger.warn(f"Customer{saved_customer.to_dict()} already exists in db")
            return saved_customer
        logger.info(f"Saving Customer{customer.to_dict()} in db")
        customer.uid = user.uid
        return await self.create(customer)

    async def patch_customer(self, customer_id: UUID, changed_customer: Customer, user: User) -> Customer:
        """Частичное обновление сущности Customer."""
        update_data = {
            attribute: value
            for attribute, value in changed_customer.to_dict(
                exclude={"customer_id", "vehicles", "uid", "created_at", "updated_at"}
            ).items()
            if value is not None
        }
        customer = await self.get_customer_by_customer_id(customer_id)
        if customer.uid != user.uid:
            logger.warn(f"User{user.model_dump()} can't patch Customer{customer.to_dict()}.")
            error_message = "Вы не можете редактировать профиль другого автовладельца."
            raise CustomerBelongsToAnotherUserError(error_message)
        logger.info(f"Updating Customer{customer.to_dict()} in db. New data={update_data}")
        return await self.update(data=update_data, item_id=customer.customer_id)


async def provide_customer_service(db_session: AsyncSession) -> AsyncGenerator[CustomerService]:
    """Возвращает CustomerService."""
    async with CustomerService.new(session=db_session) as service:
        yield service
