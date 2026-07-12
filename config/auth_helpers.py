"""Vérification du rôle côté API (header X-SGHL-Email envoyé par le frontend connecté)."""
from ninja.errors import HttpError
from django.contrib.auth import get_user_model

User = get_user_model()


def get_api_user(request):
    email = (request.headers.get('X-SGHL-Email') or '').strip().lower()
    if not email:
        return None
    return User.objects.filter(email__iexact=email).first()


def require_admin(request):
    user = get_api_user(request)
    if not user or user.role != 'ADMIN':
        raise HttpError(403, "Seul l'administrateur peut modifier la structure du système.")
    return user


def require_redirect_manager(request):
    """Pause / redirections opérationnelles — pas la structure."""
    user = get_api_user(request)
    if not user:
        raise HttpError(401, 'Connexion requise.')
    if user.role in ('ADMIN', 'SECRETAIRE_GENERALE', 'SECRETAIRE'):
        return user
    raise HttpError(403, 'Droits insuffisants pour cette action.')
