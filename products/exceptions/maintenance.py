"""Модуль с исключениями для сущности Maintenance."""

from products.exceptions.base import BaseCustomError


class ProvidedMaintenanceTypeNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем типе обслуживания."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProvidedMaintenanceNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем обслуживании."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProvidedMaintenanceCountryAssociationNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующей связи между предоставляемым обслуживанием и страной."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProvidedMaintenanceVehicleBrandAssociationAlreadyExistsError(BaseCustomError):
    """Исключение, возникающее при несуществующей связи между предоставляемым обслуживанием и маркой ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ProvidedMaintenanceCountryAssociationAlreadyExistsError(BaseCustomError):
    """Исключение, возникающее при уже существующей связи между предоставляемым обслуживанием и страной."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
