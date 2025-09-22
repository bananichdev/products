"""Модуль с конфигурацией pytest."""

import os
from abc import ABC
from collections.abc import AsyncGenerator, Generator
from typing import TypeVar

import pytest
from advanced_alchemy.base import AdvancedDeclarativeBase, orm_registry
from advanced_alchemy.config import SQLAlchemyAsyncConfig
from sqlalchemy import JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from products.models import *  # noqa: F403 Импорты нужны для инициализации моделей SQLAlchemy
from products.models.autoservice import AutoserviceUser, AutoserviceUserPermissions
from products.services.autoservice import AutoserviceService, AutoserviceUserService, BaseAutoserviceService
from products.services.customer import CustomerService
from products.services.mechanic import MechanicService


class TestAutoserviceUser(AutoserviceUser):
    """Тестовая связь пользователей с автосервисами и их ролями."""

    __table_args__ = {"extend_existing": True}

    test_permissions: Mapped[list[AutoserviceUserPermissions]] = mapped_column(
        "permissions", JSON, nullable=False, default=[]
    )


ModelType = TypeVar("ModelType", bound=AdvancedDeclarativeBase)
T = TypeVar("T")


class FixtureRequest[T](pytest.FixtureRequest, ABC):
    """Фикстура для получения типизированного параметра."""

    param: T


@pytest.fixture
def test_db_path() -> Generator[str]:
    """Путь до тестовой in-memory БД."""
    path = "/tmp/test_db.sqlite"  # noqa: S108 Используем /tmp/ для тестовых данных
    os.makedirs(os.path.dirname(path), exist_ok=True)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
async def test_sqlalchemy_config(test_db_path: str) -> SQLAlchemyAsyncConfig:
    """Тестовый SQLAlchemyAsyncConfig."""
    return SQLAlchemyAsyncConfig(
        connection_string=f"sqlite+aiosqlite:///{test_db_path}",
    )


@pytest.fixture(autouse=True)
async def create_test_tables(test_sqlalchemy_config: SQLAlchemyAsyncConfig) -> AsyncGenerator[None]:
    """Фикстура для создания всех таблиц перед началом тестовой сессии."""
    engine = test_sqlalchemy_config.get_engine()
    async with engine.begin() as connection:
        await connection.run_sync(orm_registry.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(orm_registry.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_db_session(test_sqlalchemy_config: SQLAlchemyAsyncConfig) -> AsyncGenerator[AsyncSession]:
    """Сессия для тестовой БД."""
    async with test_sqlalchemy_config.get_session() as session:
        yield session


@pytest.fixture
async def test_entity[ModelType: AdvancedDeclarativeBase](
    request: FixtureRequest[ModelType], test_db_session: AsyncSession
) -> AsyncGenerator[ModelType]:
    """Тестовая сущность."""
    entity = request.param
    test_db_session.add(entity)
    await test_db_session.commit()
    await test_db_session.refresh(entity)

    try:
        yield entity
    finally:
        entity = await test_db_session.merge(entity)
        await test_db_session.delete(entity)
        await test_db_session.commit()


@pytest.fixture
async def test_customer_service(test_db_session: AsyncSession) -> AsyncGenerator[CustomerService]:
    """Тестовый CustomerService."""
    async with CustomerService.new(session=test_db_session) as service:
        yield service


@pytest.fixture
async def test_mechanic_service(test_db_session: AsyncSession) -> AsyncGenerator[MechanicService]:
    """Тестовый MechanicService."""
    async with MechanicService.new(session=test_db_session) as service:
        yield service


@pytest.fixture
async def test_autoservice_user_service(test_db_session: AsyncSession) -> AsyncGenerator[AutoserviceUserService]:
    """Тестовый AutoserviceUserService."""
    async with AutoserviceUserService.new(session=test_db_session) as service:
        yield service


@pytest.fixture
async def test_base_autoservice_service(test_db_session: AsyncSession) -> AsyncGenerator[BaseAutoserviceService]:
    """Тестовый BaseAutoserviceService."""
    async with BaseAutoserviceService.new(session=test_db_session) as service:
        yield service


@pytest.fixture
def test_autoservice_service(
    test_autoservice_user_service: AutoserviceUserService, test_base_autoservice_service: BaseAutoserviceService
) -> AutoserviceService:
    """Тестовый AutoserviceService."""
    return AutoserviceService(
        autoservice_user_service=test_autoservice_user_service, base_autoservice_service=test_base_autoservice_service
    )
