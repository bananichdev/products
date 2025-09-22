"""Модуль с базовым классом для всех кастомных исключений."""

from abc import ABC


class BaseCustomError(Exception, ABC):
    """Базовый класс для всех кастомных исключений."""
