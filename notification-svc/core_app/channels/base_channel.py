from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import Notification


class NotificationSender(ABC):
    """Component interface for the Decorator pattern."""

    @abstractmethod
    def send(self, notification: 'Notification') -> bool:
        pass


class NotificationSenderDecorator(NotificationSender):
    """Base decorator that wraps a NotificationSender and delegates by default."""

    def __init__(self, wrapped: NotificationSender) -> None:
        self._wrapped = wrapped

    def send(self, notification: 'Notification') -> bool:
        return self._wrapped.send(notification)
