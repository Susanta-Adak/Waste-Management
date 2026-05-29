from .email_channel import EmailChannel
from .sms_channel import SMSChannel
from .push_channel import PushChannel
from .logging_decorator import LoggingDecorator
from .retry_decorator import RetryDecorator
from .base_channel import NotificationSender
from ..models import NotificationChannel, Notification


def build_channel(notification: Notification) -> NotificationSender:
    """
    Factory: returns the concrete channel for a notification, wrapped with
    Retry (inner) and Logging (outer) decorators.
    """
    if notification.channel == NotificationChannel.EMAIL:
        base: NotificationSender = EmailChannel()
    elif notification.channel == NotificationChannel.SMS:
        base = SMSChannel()
    elif notification.channel == NotificationChannel.PUSH:
        base = PushChannel()
    else:
        raise ValueError(f"Unknown notification channel: {notification.channel}")

    return LoggingDecorator(RetryDecorator(base, max_retries=3, delay=1.0))
