from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Notification


class NotificationStrategy(ABC):
    """Defines how a notification is dispatched (immediately, batched, etc.)."""

    @abstractmethod
    def execute(self, notification: 'Notification') -> None:
        pass
