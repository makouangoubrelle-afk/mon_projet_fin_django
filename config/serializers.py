"""Helpers de sérialisation pour les réponses API Django Ninja."""


def iso(value):
    if value is None:
        return None
    if hasattr(value, 'isoformat'):
        return value.isoformat()
    return str(value)
