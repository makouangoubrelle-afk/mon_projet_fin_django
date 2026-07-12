"""Vues utilitaires — SPA Vue en production (Render)."""
import mimetypes
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse


def healthz(request):
    frontend_ok = (Path(settings.FRONTEND_DIR) / 'index.html').is_file()
    mobile_ok = (Path(settings.MOBILE_DIR) / 'index.html').is_file()
    return HttpResponse(
        f'ok frontend={"yes" if frontend_ok else "no"} mobile={"yes" if mobile_ok else "no"}'
    )


def serve_spa(request, path=''):
    """Sert les fichiers Vite (assets, icons…) ou index.html pour le routeur Vue."""
    frontend_dir = Path(settings.FRONTEND_DIR)
    index = frontend_dir / 'index.html'

    if not index.is_file():
        return HttpResponse(
            (
                '<html><body style="font-family:sans-serif;padding:2rem">'
                '<h1>SGHL — Backend actif</h1>'
                '<p>Frontend en cours de compilation… Relancez le déploiement Render.</p>'
                '<p>API : <a href="/api/docs">/api/docs</a></p>'
                '</body></html>'
            ),
            content_type='text/html',
            status=503,
        )

    root = frontend_dir.resolve()
    safe_path = (path or '').lstrip('/')
    if safe_path:
        target = (frontend_dir / safe_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise Http404() from exc
        if target.is_file():
            content_type, _ = mimetypes.guess_type(str(target))
            return FileResponse(
                open(target, 'rb'),
                content_type=content_type or 'application/octet-stream',
            )

    return FileResponse(open(index, 'rb'), content_type='text/html')


def serve_mobile(request, path=''):
    """Sert l'application Flutter Web (patient) sous /mobile/."""
    mobile_dir = Path(settings.MOBILE_DIR)
    index = mobile_dir / 'index.html'

    if not index.is_file():
        return HttpResponse(
            (
                '<html><body style="font-family:sans-serif;padding:2rem;background:#0f172a;color:#e2e8f0">'
                '<h1>SGHL Mobile</h1>'
                '<p>Application Flutter en cours de compilation… Relancez le déploiement Render.</p>'
                '<p>Interface web : <a href="/" style="color:#2dd4bf">/</a></p>'
                '</body></html>'
            ),
            content_type='text/html',
            status=503,
        )

    root = mobile_dir.resolve()
    safe_path = (path or '').lstrip('/')
    if safe_path:
        target = (mobile_dir / safe_path).resolve()
        try:
            target.relative_to(root)
        except ValueError as exc:
            raise Http404() from exc
        if target.is_file():
            content_type, _ = mimetypes.guess_type(str(target))
            return FileResponse(
                open(target, 'rb'),
                content_type=content_type or 'application/octet-stream',
            )

    return FileResponse(open(index, 'rb'), content_type='text/html')
