"""Модуль с исключениями для сущности Vehicle."""

from products.exceptions.base import BaseCustomError


class VehicleNotFoundError(BaseCustomError):
    """Исключение, возникающее при отсутствии ТС в БД."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VehicleBrandNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующей марке ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VehicleModelNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующей модели ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VehicleGenerationNotFoundError(BaseCustomError):
    """Исключение, возникающее при несуществующем поколении ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VehicleModelDoesntMatchWithVehicleBrandError(BaseCustomError):
    """Исключение, возникающее при несоответствии марки и модели ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VehicleGenerationDoesntMatchWithVehicleModelError(BaseCustomError):
    """Исключение, возникающее при несоответствии модели и поколения ТС."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
