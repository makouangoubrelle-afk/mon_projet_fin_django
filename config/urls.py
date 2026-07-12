from django.contrib import admin
from django.urls import path, re_path
from api import api
from config.views import healthz, serve_spa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz),
    path('api/', api.urls),
    # Application Vue — fichiers statiques + fallback SPA (login, dashboard, etc.)
    re_path(r'^(?P<path>.*)$', serve_spa),
]
