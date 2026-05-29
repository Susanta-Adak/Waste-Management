from rest_framework import serializers
from .models import Notification, NotificationPreference, NotificationTemplate


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'recipient_id', 'recipient_contact',
            'channel', 'subject', 'message', 'status', 'error_message',
            'metadata', 'created_at', 'sent_at',
        ]
        read_only_fields = fields


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'user_id', 'notification_type', 'channel', 'is_enabled', 'updated_at']
        read_only_fields = ['id', 'updated_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'channel',
            'subject_template', 'body_template', 'is_active', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class SendNotificationSerializer(serializers.Serializer):
    notification_type = serializers.ChoiceField(choices=['WASTE_COLLECTION', 'BIN_FULL', 'PAYMENT', 'ALERT', 'SYSTEM'])
    recipient_id = serializers.CharField()
    metadata = serializers.DictField(required=False, default=dict)
