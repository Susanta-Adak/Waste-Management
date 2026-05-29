from abc import ABC, abstractmethod


class EventObserver(ABC):
    """Receives and reacts to a domain event from the Event Bus."""

    @abstractmethod
    def on_event(self, event_type: str, payload: dict) -> None:
        pass


class EventSubject(ABC):
    """Publishes domain events to all registered observers (Observer pattern)."""

    def __init__(self) -> None:
        self._observers: list[EventObserver] = []

    def attach(self, observer: EventObserver) -> None:
        self._observers.append(observer)

    def detach(self, observer: EventObserver) -> None:
        self._observers.remove(observer)

    def notify(self, event_type: str, payload: dict) -> None:
        for observer in self._observers:
            observer.on_event(event_type, payload)
