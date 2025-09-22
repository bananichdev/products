"""Модуль с тестами AutoserviceService."""

import json
from datetime import datetime
from uuid import UUID

import pytest

from products.exceptions.autoservice import (
    AutoserviceNotFoundError,
    AutoserviceUserDoesntHavePermissionsError,
    AutoserviceUserNotFoundError,
)
from products.models import Autoservice, AutoserviceUser, AutoserviceUserPermissions, User
from products.services.autoservice import AutoserviceService, AutoserviceUserService, BaseAutoserviceService


@pytest.mark.parametrize(
    "test_entity",
    [
        AutoserviceUser(uid=UUID(int=0), autoservice_id=UUID(int=0), permissions=list(AutoserviceUserPermissions)),
    ],
    indirect=["test_entity"],
)
async def test_autoservice_user_service_get_autoservice_user_by_uid_and_autoservice_id(
    test_autoservice_user_service: AutoserviceUserService,
    test_entity: AutoserviceUser,
) -> None:
    """Тест метода получения AutoserviceUser по autoservice_id и uid."""
    autoservice_user = await test_autoservice_user_service.get_autoservice_user_by_uid_and_autoservice_id(
        uid=test_entity.uid, autoservice_id=test_entity.autoservice_id
    )
    assert autoservice_user == test_entity


@pytest.mark.parametrize(
    ("test_entity", "user"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
    indirect=["test_entity"],
)
async def test_autoservice_user_service_create_autoservice_owner(
    test_autoservice_user_service: AutoserviceUserService, test_entity: Autoservice, user: User
) -> None:
    """Тест метода создания владельца автосервиса."""
    autoservice_user = await test_autoservice_user_service.create_autoservice_owner(autoservice=test_entity, user=user)
    assert autoservice_user.autoservice_id == test_entity.autoservice_id
    assert autoservice_user.uid == user.uid
    assert json.loads(str(autoservice_user.permissions)) == [
        permission.value for permission in AutoserviceUserPermissions
    ]


@pytest.mark.parametrize(
    "test_entity",
    [
        Autoservice(
            autoservice_id=UUID(int=0),
            name="Test",
            itn="1" * 12,
            psrn="1" * 13,
            city="Test",
            address="Test",
            created_at=datetime(year=2000, month=1, day=1),
        )
    ],
    indirect=["test_entity"],
)
async def test_base_autoservice_service_get_autoservice_by_autoservice_id(
    test_base_autoservice_service: BaseAutoserviceService, test_entity: Autoservice
) -> None:
    """Тест метода получения Autoservice по autoservice_id."""
    autoservice = await test_base_autoservice_service.get_autoservice_by_autoservice_id(
        autoservice_id=test_entity.autoservice_id
    )
    assert test_entity == autoservice


@pytest.mark.parametrize(
    "non_existent_autoservice_id",
    [UUID(int=0)],
)
async def test_base_autoservice_service_get_autoservice_by_autoservice_id_autoservice_not_found_error(
    test_base_autoservice_service: BaseAutoserviceService, non_existent_autoservice_id: UUID
) -> None:
    """Тест метода получения Autoservice по autoservice_id, когда Autoservice не найден."""
    with pytest.raises(AutoserviceNotFoundError):
        await test_base_autoservice_service.get_autoservice_by_autoservice_id(
            autoservice_id=non_existent_autoservice_id
        )


@pytest.mark.parametrize(
    "autoservice",
    [
        Autoservice(
            autoservice_id=UUID(int=0),
            name="Test",
            itn="1" * 12,
            psrn="1" * 13,
            city="Test",
            address="Test",
            created_at=datetime(year=2000, month=1, day=1),
        )
    ],
)
async def test_base_autoservice_service_create_autoservice(
    test_base_autoservice_service: BaseAutoserviceService, autoservice: Autoservice
) -> None:
    """Тест метода создания Autoservice."""
    created_autoservice = await test_base_autoservice_service.create_autoservice(autoservice=autoservice)
    assert created_autoservice.autoservice_id == autoservice.autoservice_id


@pytest.mark.parametrize(
    ("test_entity", "changed_autoservice"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Update test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
        )
    ],
    indirect=["test_entity"],
)
async def test_base_autoservice_service_update_autoservice(
    test_base_autoservice_service: BaseAutoserviceService, test_entity: Autoservice, changed_autoservice: Autoservice
) -> None:
    """Тест метода обновления Autoservice."""
    autoservice = await test_base_autoservice_service.update_autoservice(
        autoservice_id=test_entity.autoservice_id, changed_autoservice=changed_autoservice.to_dict()
    )
    assert autoservice.name == changed_autoservice.name


@pytest.mark.parametrize(
    "test_entity",
    [
        Autoservice(
            autoservice_id=UUID(int=0),
            name="Test",
            itn="1" * 12,
            psrn="1" * 13,
            city="Test",
            address="Test",
            created_at=datetime(year=2000, month=1, day=1),
        )
    ],
    indirect=["test_entity"],
)
async def test_get_autoservice_by_autoservice_id(
    test_autoservice_service: AutoserviceService, test_entity: Autoservice
) -> None:
    """Тест метода получения Autoservice по autoservice_id."""
    autoservice = await test_autoservice_service.get_autoservice_by_autoservice_id(
        autoservice_id=test_entity.autoservice_id
    )
    assert test_entity == autoservice


@pytest.mark.parametrize(
    "non_existent_autoservice_id",
    [UUID(int=0)],
)
async def test_get_autoservice_by_autoservice_id_autoservice_not_found_error(
    test_autoservice_service: AutoserviceService, non_existent_autoservice_id: UUID
) -> None:
    """Тест метода получения Autoservice по autoservice_id, когда Autoservice не найден."""
    with pytest.raises(AutoserviceNotFoundError):
        await test_autoservice_service.get_autoservice_by_autoservice_id(autoservice_id=non_existent_autoservice_id)


@pytest.mark.parametrize(
    ("autoservice", "user"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        )
    ],
)
async def test_create_autoservice(
    test_autoservice_service: AutoserviceService,
    test_autoservice_user_service: AutoserviceUserService,
    autoservice: Autoservice,
    user: User,
) -> None:
    """Тест метода создания Autoservice с AutoserviceUser."""
    created_autoservice = await test_autoservice_service.create_autoservice(autoservice=autoservice, user=user)
    autoservice_user = await test_autoservice_user_service.get_autoservice_user_by_uid_and_autoservice_id(
        autoservice_id=created_autoservice.autoservice_id, uid=user.uid
    )
    assert created_autoservice.autoservice_id == autoservice.autoservice_id
    assert autoservice_user.uid == user.uid
    assert json.loads(str(autoservice_user.permissions)) == [
        permission.value for permission in AutoserviceUserPermissions
    ]


@pytest.mark.parametrize(
    ("autoservice", "user"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
)
async def test_validate_autoservice_manage_provided_maintenance_permissions_autoservice_user_not_found_error(
    test_autoservice_service: AutoserviceService, autoservice: Autoservice, user: User
) -> None:
    """Тест метода проверки прав у AutoserviceUser, когда AutoserviceUser не найден."""
    with pytest.raises(AutoserviceUserNotFoundError):
        await test_autoservice_service.validate_autoservice_manage_provided_maintenance_permissions(
            autoservice=autoservice, user=user
        )


@pytest.mark.parametrize(
    ("test_entity", "autoservice", "user"),
    [
        (
            AutoserviceUser(uid=UUID(int=0), autoservice_id=UUID(int=0), permissions=[]),
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
    indirect=["test_entity"],
)
async def test_validate_autoservice_manage_provided_maintenance_permissions(
    test_autoservice_service: AutoserviceService, test_entity: AutoserviceUser, autoservice: Autoservice, user: User
) -> None:
    """Тест метода проверки права autoservice:manage_provided_maintenance у AutoserviceUser."""
    test_entity.permissions = json.loads(str(test_entity.permissions))
    with pytest.raises(AutoserviceUserDoesntHavePermissionsError):
        await test_autoservice_service.validate_autoservice_manage_provided_maintenance_permissions(
            autoservice=autoservice, user=user
        )


@pytest.mark.parametrize(
    ("test_entity", "changed_autoservice", "user"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Patch test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
    indirect=["test_entity"],
)
async def test_patch_autoservice(
    test_autoservice_service: AutoserviceService,
    test_autoservice_user_service: AutoserviceUserService,
    test_entity: Autoservice,
    changed_autoservice: Autoservice,
    user: User,
) -> None:
    """Тест метода изменения Autoservice."""
    autoservice_user = await test_autoservice_user_service.create_autoservice_owner(autoservice=test_entity, user=user)
    autoservice_user.permissions = list(AutoserviceUserPermissions)
    autoservice = await test_autoservice_service.patch_autoservice(
        autoservice_id=test_entity.autoservice_id, user=user, changed_autoservice=changed_autoservice
    )
    assert autoservice.name == changed_autoservice.name


@pytest.mark.parametrize(
    ("test_entity", "changed_autoservice", "user"),
    [
        (
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            Autoservice(
                autoservice_id=UUID(int=0),
                name="Patch test",
                itn="1" * 12,
                psrn="1" * 13,
                city="Test",
                address="Test",
                created_at=datetime(year=2000, month=1, day=1),
            ),
            User(uid=UUID(int=0)),
        ),
    ],
    indirect=["test_entity"],
)
async def test_patch_autoservice_autoservice_user_doesnt_have_permissions_error(
    test_autoservice_service: AutoserviceService,
    test_autoservice_user_service: AutoserviceUserService,
    test_entity: Autoservice,
    changed_autoservice: Autoservice,
    user: User,
) -> None:
    """Тест метода изменения Autoservice."""
    autoservice_user = await test_autoservice_user_service.create_autoservice_owner(autoservice=test_entity, user=user)
    autoservice_user.permissions = []
    with pytest.raises(AutoserviceUserDoesntHavePermissionsError):
        await test_autoservice_service.patch_autoservice(
            autoservice_id=test_entity.autoservice_id, user=user, changed_autoservice=changed_autoservice
        )
