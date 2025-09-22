"""Модуль с MechanicService."""

from collections.abc import AsyncGenerator
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.mechanic import (
    MechanicBelongsToAnotherUserError,
    MechanicNotFoundError,
)
from products.models.mechanic import Mechanic
from products.models.user import User
from products.settings import logger


class MechanicRepository(SQLAlchemyAsyncRepository[Mechanic]):  # type: ignore[type-var]
    """MechanicRepository для взаимодействия с БД."""

    id_attribute = "mechanic_id"
    model_type = Mechanic


class MechanicService(SQLAlchemyAsyncRepositoryService[Mechanic]):  # type: ignore[type-var]
    """MechanicService для бизнес-логики."""

    repository_type = MechanicRepository

    @staticmethod
    def validate_mechanic_owner(mechanic: Mechanic, user: User) -> None:
        """Валидация пользователя-владельца сущности Mechanic."""
        if mechanic.uid != user.uid:
            logger.warn(f"Mechanic belongs to User with uid={mechanic.uid}, but User{user.model_dump()} try manage it")
            error_message = "Вы не можете менять данные другого механика."
            raise MechanicBelongsToAnotherUserError(error_message)

    async def get_mechanic_by_mechanic_id(self, mechanic_id: UUID) -> Mechanic:
        """Получение Mechanic по mechanic_id."""
        if (mechanic := await self.get_one_or_none(Mechanic.mechanic_id == mechanic_id)) is None:
            logger.warn(f"Mechanic with {mechanic_id=} doesn't exists in db")
            error_message = "Механик не найден."
            raise MechanicNotFoundError(error_message)
        return mechanic

    async def create_mechanic(self, mechanic: Mechanic, user: User) -> Mechanic:
        """Создание сущности Mechanic."""
        if (saved_mechanic := await self.get_one_or_none(Mechanic.uid == user.uid)) is not None:
            logger.warn(f"Mechanic{saved_mechanic.to_dict()} already exists in db")
            return saved_mechanic
        logger.info(f"Saving Mechanic{mechanic.to_dict()} in db")
        mechanic.uid = user.uid
        return await self.create(mechanic)

    async def patch_mechanic(self, mechanic_id: UUID, changed_mechanic: Mechanic, user: User) -> Mechanic:
        """Частичное обновление сущности Mechanic."""
        update_data = {
            key: value
            for key, value in changed_mechanic.to_dict(
                exclude={"mechanic_id", "uid", "autoservices", "provided_maintenance", "created_at", "updated_at"}
            ).items()
            if value is not None
        }
        mechanic = await self.get_mechanic_by_mechanic_id(mechanic_id)
        if mechanic.uid != user.uid:
            logger.warn(f"User{user.model_dump()} can't patch Mechanic{mechanic.to_dict()}.")
            error_message = "Вы не можете редактировать профиль другого механика."
            raise MechanicBelongsToAnotherUserError(error_message)
        logger.info(f"Updating Mechanic{mechanic.to_dict()} in db. New data={update_data}")
        return await self.update(data=update_data, item_id=mechanic.mechanic_id)


async def provide_mechanic_service(db_session: AsyncSession) -> AsyncGenerator[MechanicService]:
    """Возвращает MechanicService."""
    async with MechanicService.new(session=db_session) as service:
        yield service
