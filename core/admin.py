from django.contrib import admin
from .models import HospitalSettings, LoginHistory, ActivityLog, Notification


@admin.register(HospitalSettings)
class HospitalSettingsAdmin(admin.ModelAdmin):
    list_display = ('nom_hopital', 'telephone', 'email', 'updated_at')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'success', 'ip_address', 'created_at')
    list_filter = ('success', 'role')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('email', 'action', 'module', 'created_at')
    search_fields = ('email', 'action', 'detail')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'level', 'is_read', 'created_at')
