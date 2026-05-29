import logging
import threading
import time
from collections import defaultdict

from .base_strategy import NotificationStrategy
from ..channels import build_channel
from ..models import Notification

logger = logging.getLogger(__name__)


class BatchStrategy(NotificationStrategy):
    """
    Collects notifications for a window_seconds interval then flushes them in
    one pass, reducing burst load on external providers.
    """

    def __init__(self, window_seconds: float = 60.0) -> None:
        self._window = window_seconds
        self._queue: list[str] = []  # notification PKs
        self._lock = threading.Lock()
        self._timer: threading.Timer | None = None

    def execute(self, notification: Notification) -> None:
        with self._lock:
            self._queue.append(str(notification.id))
            if self._timer is None:
                self._timer = threading.Timer(self._window, self._flush)
                self._timer.daemon = True
                self._timer.start()

    def _flush(self) -> None:
        with self._lock:
            ids, self._queue = self._queue[:], []
            self._timer = None

        notifications = Notification.objects.filter(id__in=ids)
        for notification in notifications:
            try:
                channel = build_channel(notification)
                channel.send(notification)
            except Exception:
                logger.exception("Batch flush failed for notification %s", notification.id)
