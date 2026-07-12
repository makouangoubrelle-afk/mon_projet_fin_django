from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Informations SGHL", {"fields": ("role", "telephone", "service", "en_pause")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Informations SGHL", {"fields": ("role", "telephone", "service")}),
    )
    list_display = ["username", "email", "telephone", "role", "is_staff"]
