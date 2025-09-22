"""Модуль с тестами MechanicService."""

from datetime import datetime
from uuid import UUID

import pytest

from products.exceptions.mechanic import MechanicBelongsToAnotherUserError, MechanicNotFoundError
from products.models import User
from products.models.mechanic import Mechanic
from products.services.mechanic import MechanicService


@pytest.mark.parametrize(
    "test_entity",
    [
        Mechanic(
            mechanic_id=UUID(int=0),
            name="Test",
            city="Test",
            private=True,
            mobile=True,
            uid=UUID(int=0),
            created_at=datetime(year=2000, month=1, day=1),
        )
    ],
    indirect=["test_entity"],
)
async def test_get_mechanic_by_mechanic_id(test_mechanic_service: MechanicService, test_entity: Mechanic) -> None:
    """Тест получения Mechanic по mechanic_id."""
    mechanic = await test_mechanic_service.get_mechanic_by_mechanic_id(mechanic_id=test_entity.mechanic_id)
    assert test_entity == mechanic


@pytest.mark.parametrize("non_existent_mechanic_id", [UUID(int=0)])
async def test_get_mechanic_by_mechanic_id_mechanic_not_found_error(
    test_mechanic_service: MechanicService, non_existent_mechanic_id: UUID
) -> None:
    """Тест получения Mechanic по mechanic_id, когда Mechanic не найден."""
    with pytest.raises(MechanicNotFoundError):
        await test_mechanic_service.get_mechanic_by_mechanic_id(mechanic_id=non_existent_mechanic_id)


@pytest.mark.parametrize(
    ("mechanic", "user"),
    [
        (
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Test",
                city="Test",
                private=True,
                mobile=True,
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
)
async def test_create_mechanic(test_mechanic_service: MechanicService, mechanic: Mechanic, user: User) -> None:
    """Тест создания Mechanic."""
    created_mechanic = await test_mechanic_service.create_mechanic(mechanic=mechanic, user=user)
    assert created_mechanic.mechanic_id == mechanic.mechanic_id


@pytest.mark.parametrize(
    ("test_entity", "changed_mechanic", "user"),
    [
        (
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Test",
                city="Test",
                private=True,
                mobile=True,
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Patch test",
                city="Patch test",
                private=True,
                mobile=True,
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
    indirect=["test_entity"],
)
async def test_patch_mechanic(
    test_mechanic_service: MechanicService, test_entity: Mechanic, changed_mechanic: Mechanic, user: User
) -> None:
    """Тест частичного обновления Mechanic."""
    mechanic = await test_mechanic_service.patch_mechanic(
        mechanic_id=test_entity.mechanic_id, changed_mechanic=changed_mechanic, user=user
    )
    assert mechanic.name == changed_mechanic.name
    assert mechanic.city == changed_mechanic.city


@pytest.mark.parametrize(
    ("non_existent_mechanic_id", "changed_mechanic", "user"),
    [
        (
            UUID(int=0),
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Patch test",
                city="Patch test",
                private=True,
                mobile=True,
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
)
async def test_patch_mechanic_mechanic_not_found_error(
    test_mechanic_service: MechanicService, non_existent_mechanic_id: UUID, changed_mechanic: Mechanic, user: User
) -> None:
    """Тест частичного обновления Mechanic, когда Mechanic не найден."""
    with pytest.raises(MechanicNotFoundError):
        await test_mechanic_service.patch_mechanic(
            mechanic_id=non_existent_mechanic_id, changed_mechanic=changed_mechanic, user=user
        )


@pytest.mark.parametrize(
    ("test_entity", "changed_mechanic", "user"),
    [
        (
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Test",
                city="Test",
                private=True,
                mobile=True,
                uid=UUID(int=1),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Patch test",
                city="Patch test",
                private=True,
                mobile=True,
                uid=UUID(int=0),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
    indirect=["test_entity"],
)
async def test_patch_mechanic_mechanic_belongs_to_another_user_error(
    test_mechanic_service: MechanicService, test_entity: Mechanic, changed_mechanic: Mechanic, user: User
) -> None:
    """Тест частичного обновления Mechanic, когда Mechanic принадлежит другому пользователю."""
    with pytest.raises(MechanicBelongsToAnotherUserError):
        await test_mechanic_service.patch_mechanic(
            mechanic_id=test_entity.mechanic_id, changed_mechanic=changed_mechanic, user=user
        )


@pytest.mark.parametrize(
    ("mechanic", "user"),
    [
        (
            Mechanic(
                mechanic_id=UUID(int=0),
                name="Patch test",
                city="Patch test",
                private=True,
                mobile=True,
                uid=UUID(int=1),
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
)
def test_validate_mechanic_owner_mechanic_belongs_to_another_user_error(
    test_mechanic_service: MechanicService, mechanic: Mechanic, user: User
) -> None:
    """Тест проверки владельца Mechanic, когда Mechanic принадлежит другому пользователю."""
    with pytest.raises(MechanicBelongsToAnotherUserError):
        test_mechanic_service.validate_mechanic_owner(mechanic=mechanic, user=user)
