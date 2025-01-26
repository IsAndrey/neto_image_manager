"""Определяемые исключения"""


class ExeptionEndpointAccessable(Exception):
    """Статус ответа сервиса != 200."""


class ExeptionFormatAnswer(TypeError):
    """Формат ответа не соответтсвует документации."""


class ExeptionProgramInit(Exception):
    """Переменные окружения не инициализированы."""


class ExeptionValueFound(TypeError):
    """Не найдено значение по ключу."""
