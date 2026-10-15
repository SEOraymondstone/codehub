"""Небольшие общие помощники CodeHub."""

from django.conf import settings


def human_size(num_bytes: int) -> str:
    """Человекочитаемый размер: 512 Б, 20 МБ, 1 ГБ."""
    gb = num_bytes / (1024**3)
    if gb >= 1:
        return f"{gb:g} ГБ"
    mb = num_bytes / (1024**2)
    if mb >= 1:
        return f"{mb:g} МБ"
    return f"{num_bytes} Б"


def max_upload_label() -> str:
    """Подпись лимита загрузки домашнего задания."""
    return human_size(settings.HOMEWORK_MAX_UPLOAD_SIZE)
