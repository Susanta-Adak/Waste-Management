import logging
from string import Template

from .models import (
    Notification,
    NotificationChannel,
    NotificationPreference,
    NotificationTemplate,
)
from .strategies.base_strategy import NotificationStrategy
from .strategies.immediate_strategy import ImmediateStrategy

logger = logging.getLogger(__name__)

_DEFAULT_CHANNELS = [NotificationChannel.EMAIL]


class NotificationService:
    """
    Orchestrates notification creation and dispatch.

    Uses the Strategy pattern for dispatch timing and falls back to the user's
    NotificationPreference records to determine which channels to use.
    """

    def __init__(self, strategy: NotificationStrategy | None = None) -> None:
        self._strategy = strategy or ImmediateStrategy()

    def create_and_send(
        self,
        notification_type: str,
        recipient_id: str,
        metadata: dict | None = None,
    ) -> list[Notification]:
        metadata = metadata or {}
        channels = self._resolve_channels(recipient_id, notification_type)
        created: list[Notification] = []

        for channel in channels:
            notification = self._build_notification(
                notification_type, recipient_id, channel, metadata
            )
            created.append(notification)
            try:
                self._strategy.execute(notification)
            except Exception:
                logger.exception(
                    "Strategy execute failed for notification %s", notification.id
                )

        return created

    def _resolve_channels(self, user_id: str, notification_type: str) -> list[str]:
        prefs = NotificationPreference.objects.filter(
            user_id=user_id,
            notification_type=notification_type,
            is_enabled=True,
        ).values_list('channel', flat=True)

        return list(prefs) if prefs.exists() else _DEFAULT_CHANNELS

    def _build_notification(
        self,
        notification_type: str,
        recipient_id: str,
        channel: str,
        metadata: dict,
    ) -> Notification:
        template = NotificationTemplate.objects.filter(
            notification_type=notification_type,
            channel=channel,
            is_active=True,
        ).first()

        if template:
            subject = Template(template.subject_template).safe_substitute(metadata)
            message = Template(template.body_template).safe_substitute(metadata)
        else:
            subject = f"[{notification_type}] Notification"
            message = f"You have a new {notification_type.lower().replace('_', ' ')} notification."

        return Notification.objects.create(
            notification_type=notification_type,
            recipient_id=recipient_id,
            recipient_contact=metadata.get('contact', ''),
            channel=channel,
            subject=subject,
            message=message,
            metadata=metadata,
        )
