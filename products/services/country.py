"""Модуль с сервисом сущности Country."""

from collections.abc import AsyncGenerator

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from sqlalchemy.ext.asyncio import AsyncSession

from products.exceptions.country import CountryNotFoundError
from products.models.country import Country
from products.settings import logger


class CountryRepository(
    SQLAlchemyAsyncRepository[Country]  # type: ignore[type-var]
):
    """CountryRepository для взаимодействия с БД."""

    id_attribute = "country_id"
    model_type = Country


class CountryService(
    SQLAlchemyAsyncRepositoryService[Country]  # type: ignore[type-var]
):
    """CountryService для бизнес-логики."""

    repository_type = CountryRepository

    async def get_country_by_country_id(self, country_id: int) -> Country:
        """Получить Country по country_id."""
        if (
            country := await self.get_one_or_none(
                Country.country_id == country_id,
            )
        ) is None:
            logger.warn(f"Country with {country_id=} doesn't exists in db")
            error_message = "Страна не найдена."
            raise CountryNotFoundError(error_message)
        logger.info(f"Got Country{country.to_dict()} from db")
        return country


async def provide_country_service(
    db_session: AsyncSession,
) -> AsyncGenerator[CountryService]:
    """Возвращает CountryService."""
    async with CountryService.new(session=db_session) as service:
        yield service
