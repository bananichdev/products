"""Модуль с AutoserviceService."""

from collections.abc import AsyncGenerator
from uuid import UUID

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.autoservice import (
    AutoserviceNotFoundError,
    AutoserviceUserDoesntHavePermissionsError,
    AutoserviceUserNotFoundError,
)
from products.models.autoservice import Autoservice, AutoserviceUser, AutoserviceUserPermissions
from products.models.user import User
from products.settings import logger


class AutoserviceUserRepository(SQLAlchemyAsyncRepository[AutoserviceUser]):  # type: ignore[type-var]
    """AutoserviceUserRepository для взаимодействия с БД."""

    id_attribute = "uid"
    model_type = AutoserviceUser


class AutoserviceUserService(SQLAlchemyAsyncRepositoryService[AutoserviceUser]):  # type: ignore[type-var]
    """AutoserviceUserService для бизнес-логики."""

    repository_type = AutoserviceUserRepository

    async def get_autoservice_user_by_uid_and_autoservice_id(self, uid: UUID, autoservice_id: UUID) -> AutoserviceUser:
        """Получение AutoserviceUser по uid и autoservice_id."""
        if (
            autoservice_user := await self.get_one_or_none(
                and_(AutoserviceUser.uid == uid, AutoserviceUser.autoservice_id == autoservice_id)
            )
        ) is None:
            logger.warn(f"AutoserviceUser with {uid=} and {autoservice_id=} doesn't exists in db")
            error_message = "У вас нет доступа к этому автосервису."
            raise AutoserviceUserNotFoundError(error_message)
        return autoservice_user

    async def create_autoservice_owner(self, autoservice: Autoservice, user: User) -> AutoserviceUser:
        """Создание владельца автосервиса."""
        autoservice_user = AutoserviceUser(
            uid=user.uid, autoservice_id=autoservice.autoservice_id, permissions=list(AutoserviceUserPermissions)
        )
        logger.info(f"Saving AutoserviceUser{autoservice_user.to_dict()} in db")
        return await self.create(autoservice_user)


async def provide_autoservice_user_service(db_session: AsyncSession) -> AsyncGenerator[AutoserviceUserService]:
    """Возвращает AutoserviceUserService."""
    async with AutoserviceUserService.new(session=db_session) as service:
        yield service


class AutoserviceRepository(SQLAlchemyAsyncRepository[Autoservice]):  # type: ignore[type-var]
    """AutoserviceRepository для взаимодействия с БД."""

    id_attribute = "autoservice_id"
    model_type = Autoservice


class BaseAutoserviceService(SQLAlchemyAsyncRepositoryService[Autoservice]):  # type: ignore[type-var]
    """BaseAutoserviceService для бизнес-логики."""

    repository_type = AutoserviceRepository

    async def get_autoservice_by_autoservice_id(self, autoservice_id: UUID) -> Autoservice:
        """Получение Autoservice по autoservice_id."""
        if (
            autoservice := await self.get_one_or_none(
                Autoservice.autoservice_id == autoservice_id,
            )
        ) is None:
            logger.warn(f"Autoservice with {autoservice_id=} doesn't exists in db")
            error_message = "Автосервис не найден."
            raise AutoserviceNotFoundError(error_message)
        logger.info(f"Got Autoservice{autoservice.to_dict()} from db")
        return autoservice

    async def create_autoservice(self, autoservice: Autoservice) -> Autoservice:
        """Создание сущности Autoservice."""
        # TODO: логика проверки ИНН и ОГРН # noqa: TD002, TD003
        logger.info(f"Saving Autoservice{autoservice.to_dict()} in db")
        return await self.create(autoservice)

    async def update_autoservice(self, autoservice_id: UUID, changed_autoservice: dict) -> Autoservice:
        """Обновление сущности Autoservice."""
        return await self.update(item_id=autoservice_id, data=changed_autoservice)


async def provide_base_autoservice_service(db_session: AsyncSession) -> AsyncGenerator[BaseAutoserviceService]:
    """Возвращает BaseAutoserviceService."""
    async with BaseAutoserviceService.new(session=db_session) as service:
        yield service


class AutoserviceService:
    """AutoserviceService для бизнес-логики."""

    def __init__(
        self, base_autoservice_service: BaseAutoserviceService, autoservice_user_service: AutoserviceUserService
    ) -> None:
        self.__base_autoservice_service = base_autoservice_service
        self.__autoservice_user_service = autoservice_user_service

    async def get_autoservice_by_autoservice_id(self, autoservice_id: UUID) -> Autoservice:
        """Получение Autoservice по autoservice_id."""
        return await self.__base_autoservice_service.get_autoservice_by_autoservice_id(autoservice_id=autoservice_id)

    async def create_autoservice(self, autoservice: Autoservice, user: User) -> Autoservice:
        """Создание сущности Autoservice."""
        logger.info("Creating Autoservice with owner User")
        autoservice = await self.__base_autoservice_service.create_autoservice(autoservice=autoservice)
        await self.__autoservice_user_service.create_autoservice_owner(autoservice=autoservice, user=user)
        logger.info("Autoservice and its owner was created")
        return autoservice

    async def validate_autoservice_manage_provided_maintenance_permissions(
        self, autoservice: Autoservice, user: User
    ) -> None:
        """Валидация разрешений на управление ProvidedMaintenance для сущности Autoservice."""
        autoservice_user = await self.__autoservice_user_service.get_autoservice_user_by_uid_and_autoservice_id(
            uid=user.uid, autoservice_id=autoservice.autoservice_id
        )
        if AutoserviceUserPermissions.autoservice_manage_provided_maintenance not in autoservice_user.permissions:
            logger.warn(
                f"User{user.model_dump()} doesn't have permission "
                f"{AutoserviceUserPermissions.autoservice_manage_provided_maintenance=}"
            )
            error_message = "У вас нет прав на управление обслуживаниями, которые предоставляет автосервис."
            raise AutoserviceUserDoesntHavePermissionsError(error_message)

    async def patch_autoservice(
        self, autoservice_id: UUID, user: User, changed_autoservice: Autoservice
    ) -> Autoservice:
        """Частичное обновление сущности autoservice."""
        update_data = {
            key: value
            for key, value in changed_autoservice.to_dict(
                exclude={
                    "autoservice_id",
                    "itn",
                    "psrn",
                    "address",
                    "lon",
                    "latmechanics",
                    "users",
                    "provided_maintenance",
                    "created_at",
                    "updated_at",
                }
            ).items()
            if value is not None
        }
        autoservice = await self.get_autoservice_by_autoservice_id(autoservice_id)
        autoservice_user = await self.__autoservice_user_service.get_autoservice_user_by_uid_and_autoservice_id(
            uid=user.uid, autoservice_id=autoservice.autoservice_id
        )
        if AutoserviceUserPermissions.autoservice_manage not in autoservice_user.permissions:
            logger.warn(
                f"User{user.model_dump()} doesn't have permission {AutoserviceUserPermissions.autoservice_manage=}"
            )
            error_message = "У вас нет прав на изменение данных этого автосервиса."
            raise AutoserviceUserDoesntHavePermissionsError(error_message)
        logger.info(f"Updating autoservice{autoservice.to_dict()} in db. New data={update_data}")
        return await self.__base_autoservice_service.update_autoservice(
            changed_autoservice=update_data, autoservice_id=autoservice_id
        )


async def provide_autoservice_service(
    base_autoservice_service: BaseAutoserviceService, autoservice_user_service: AutoserviceUserService
) -> AutoserviceService:
    """Возвращает AutoserviceService."""
    return AutoserviceService(
        base_autoservice_service=base_autoservice_service, autoservice_user_service=autoservice_user_service
    )
