import logging

from .base_channel import NotificationSenderDecorator
from ..models import Notification

logger = logging.getLogger(__name__)


class LoggingDecorator(NotificationSenderDecorator):
    """Decorates any channel with structured send/result logging."""

    def send(self, notification: Notification) -> bool:
        logger.info(
            "Dispatching %s via %s → recipient=%s id=%s",
            notification.notification_type,
            notification.channel,
            notification.recipient_id,
            notification.id,
        )
        result = self._wrapped.send(notification)
        logger.info("Dispatch %s: %s", notification.id, "success" if result else "failed")
        return result
