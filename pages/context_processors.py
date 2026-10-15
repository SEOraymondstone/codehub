from django.conf import settings

from codehub.utils import max_upload_label

from .models import SiteSettings


def site_settings(request):
    """Тексты и контакты сайта для всех шаблонов.

    Значения по умолчанию берутся из settings.CODEHUB_SITE, поверх них
    накладываются данные из админки (SiteSettings).
    """
    # NOTE: the variable is called "site_info" on purpose. Django's auth views
    # (LoginView, PasswordResetView, ...) put a RequestSite into the "site"
    # context variable, which would shadow our branding values.
    site = dict(settings.CODEHUB_SITE)
    try:
        site.update(SiteSettings.load().as_dict())
    except Exception:  # pragma: no cover - до применения миграций
        pass
    return {
        "site_info": site,
        "homework_max_upload": max_upload_label(),
    }
