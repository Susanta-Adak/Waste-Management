import logging
import time

from .base_channel import NotificationSenderDecorator
from ..models import Notification

logger = logging.getLogger(__name__)


class RetryDecorator(NotificationSenderDecorator):
    """Retries the wrapped channel on failure with a fixed delay."""

    def __init__(self, wrapped, max_retries: int = 3, delay: float = 1.0) -> None:
        super().__init__(wrapped)
        self._max_retries = max_retries
        self._delay = delay

    def send(self, notification: Notification) -> bool:
        for attempt in range(1, self._max_retries + 1):
            if self._wrapped.send(notification):
                return True
            if attempt < self._max_retries:
                logger.warning(
                    "Retry %d/%d for notification %s in %.1fs",
                    attempt, self._max_retries, notification.id, self._delay,
                )
                time.sleep(self._delay)
        return False
