from django.contrib import admin
from .models import Notification, NotificationTemplate, NotificationPreference


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'notification_type', 'channel', 'is_active', 'updated_at')
    list_filter = ('notification_type', 'channel', 'is_active')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_type', 'recipient_id', 'channel', 'status', 'created_at')
    list_filter = ('notification_type', 'channel', 'status')
    search_fields = ('recipient_id', 'recipient_contact')
    readonly_fields = ('id', 'created_at', 'sent_at')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'notification_type', 'channel', 'is_enabled', 'updated_at')
    list_filter = ('notification_type', 'channel', 'is_enabled')
    search_fields = ('user_id',)
