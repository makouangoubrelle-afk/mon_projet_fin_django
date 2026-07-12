"""Services transversaux : journalisation, notifications."""

from django.utils import timezone as django_timezone


def _client_ip(request) -> str | None:
    if not request:
        return None
    meta = getattr(request, 'META', None) or {}
    forwarded = meta.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return meta.get('REMOTE_ADDR')


def _client_agent(request) -> str:
    if not request:
        return ''
    meta = getattr(request, 'META', None) or {}
    return (meta.get('HTTP_USER_AGENT') or '')[:500]


def record_login(user, request, success: bool = True) -> None:
    from .models import LoginHistory

    LoginHistory.objects.create(
        user=user if success else None,
        email=user.email if user else '',
        role=user.role if user else '',
        ip_address=_client_ip(request),
        user_agent=_client_agent(request),
        success=success,
    )
    if success and user:
        user.last_login = django_timezone.now()
        user.save(update_fields=['last_login'])


def log_activity(request, action: str, module: str = '', detail: str = '', user=None) -> None:
    from config.auth_helpers import get_api_user
    from .models import ActivityLog

    actor = user or get_api_user(request)
    ActivityLog.objects.create(
        user=actor,
        email=actor.email if actor else '',
        role=actor.role if actor else '',
        action=action,
        module=module,
        detail=detail[:2000] if detail else '',
    )


def notify_user(user, title: str, message: str, level: str = 'INFO', link: str = '') -> None:
    from .models import Notification

    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        level=level,
        link=link,
    )


def notify_broadcast(title: str, message: str, level: str = 'INFO', link: str = '') -> None:
    from .models import Notification

    Notification.objects.create(
        user=None,
        title=title,
        message=message,
        level=level,
        link=link,
    )
