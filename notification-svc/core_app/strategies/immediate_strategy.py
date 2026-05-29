from .base_strategy import NotificationStrategy
from ..channels import build_channel
from ..models import Notification


class ImmediateStrategy(NotificationStrategy):
    """Sends the notification synchronously in the current thread."""

    def execute(self, notification: Notification) -> None:
        channel = build_channel(notification)
        channel.send(notification)
