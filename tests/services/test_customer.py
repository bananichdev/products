"""Модуль с тестами CustomerService."""

from datetime import datetime
from uuid import UUID

import pytest

from products.exceptions.customer import CustomerBelongsToAnotherUserError, CustomerNotFoundError
from products.models.customer import Customer
from products.models.user import User
from products.services.customer import CustomerService


@pytest.mark.parametrize(
    "test_entity",
    [Customer(customer_id=UUID(int=0), name="Test", uid=UUID(int=0), created_at=datetime(year=2000, month=1, day=1))],
    indirect=["test_entity"],
)
async def test_get_customer_by_customer_id(test_customer_service: CustomerService, test_entity: Customer) -> None:
    """Тест получения Customer по customer_id."""
    customer = await test_customer_service.get_customer_by_customer_id(customer_id=test_entity.customer_id)
    assert test_entity == customer


@pytest.mark.parametrize("non_existent_customer_id", [UUID(int=0)])
async def test_get_customer_by_customer_id_customer_not_found_error(
    test_customer_service: CustomerService, non_existent_customer_id: UUID
) -> None:
    """Тест получения Customer по customer_id, когда Customer не найден."""
    with pytest.raises(CustomerNotFoundError):
        await test_customer_service.get_customer_by_customer_id(customer_id=non_existent_customer_id)


@pytest.mark.parametrize(
    ("customer", "user"),
    [
        (
            Customer(
                customer_id=UUID(int=0), name="Test", uid=UUID(int=0), created_at=datetime(year=2000, month=1, day=1)
            ),
            User(uid=UUID(int=0)),
        ),
    ],
)
async def test_create_customer(test_customer_service: CustomerService, customer: Customer, user: User) -> None:
    """Тест создания Customer."""
    created_customer = await test_customer_service.create_customer(customer=customer, user=user)
    assert created_customer.customer_id == customer.customer_id


@pytest.mark.parametrize(
    ("test_entity", "changed_customer", "user"),
    [
        (
            Customer(
                customer_id=UUID(int=0), name="Test", uid=UUID(int=0), created_at=datetime(year=2000, month=1, day=1)
            ),
            Customer(
                customer_id=UUID(int=0),
                name="Patch test",
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
    indirect=["test_entity"],
)
async def test_patch_customer(
    test_customer_service: CustomerService, test_entity: Customer, changed_customer: Customer, user: User
) -> None:
    """Тест частичного обновления Customer."""
    customer = await test_customer_service.patch_customer(
        customer_id=test_entity.customer_id, changed_customer=changed_customer, user=user
    )
    assert customer.name == changed_customer.name


@pytest.mark.parametrize(
    ("non_existent_customer_id", "changed_customer", "user"),
    [
        (
            UUID(int=0),
            Customer(
                customer_id=UUID(int=0),
                name="Patch test",
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
)
async def test_patch_customer_customer_not_found_error(
    test_customer_service: CustomerService, non_existent_customer_id: UUID, changed_customer: Customer, user: User
) -> None:
    """Тест частичного обновления Customer, когда Customer не найден."""
    with pytest.raises(CustomerNotFoundError):
        await test_customer_service.patch_customer(
            customer_id=non_existent_customer_id, changed_customer=changed_customer, user=user
        )


@pytest.mark.parametrize(
    ("test_entity", "changed_customer", "user"),
    [
        (
            Customer(
                customer_id=UUID(int=0), name="Test", uid=UUID(int=1), created_at=datetime(year=2000, month=1, day=1)
            ),
            Customer(
                customer_id=UUID(int=0),
                name="Patch test",
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
    indirect=["test_entity"],
)
async def test_patch_customer_customer_belongs_to_another_user_error(
    test_customer_service: CustomerService, test_entity: Customer, changed_customer: Customer, user: User
) -> None:
    """Тест частичного обновления Customer, когда Customer принадлежит другому пользователю."""
    with pytest.raises(CustomerBelongsToAnotherUserError):
        await test_customer_service.patch_customer(
            customer_id=test_entity.customer_id, changed_customer=changed_customer, user=user
        )
