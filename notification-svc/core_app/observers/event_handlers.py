import logging

from .base_observer import EventObserver

logger = logging.getLogger(__name__)

# Event type constants published by the Event Bus
EVENT_BIN_FULL = 'BIN_FULL'
EVENT_WASTE_COLLECTION_COMPLETED = 'WASTE_COLLECTION_COMPLETED'
EVENT_PAYMENT_PROCESSED = 'PAYMENT_PROCESSED'
EVENT_ALERT = 'ALERT'


class BinFullEventHandler(EventObserver):
    """Notifies the assigned collector when a smart bin reaches capacity."""

    def __init__(self, notification_service) -> None:
        self._service = notification_service

    def on_event(self, event_type: str, payload: dict) -> None:
        if event_type != EVENT_BIN_FULL:
            return
        logger.info("BIN_FULL event received for bin %s", payload.get('bin_id'))
        self._service.create_and_send(
            notification_type='BIN_FULL',
            recipient_id=payload.get('collector_id', ''),
            metadata=payload,
        )


class WasteCollectionEventHandler(EventObserver):
    """Notifies the resident when their waste has been collected."""

    def __init__(self, notification_service) -> None:
        self._service = notification_service

    def on_event(self, event_type: str, payload: dict) -> None:
        if event_type != EVENT_WASTE_COLLECTION_COMPLETED:
            return
        logger.info("WASTE_COLLECTION_COMPLETED event for user %s", payload.get('user_id'))
        self._service.create_and_send(
            notification_type='WASTE_COLLECTION',
            recipient_id=payload.get('user_id', ''),
            metadata=payload,
        )


class PaymentEventHandler(EventObserver):
    """Notifies the user when a payment has been processed."""

    def __init__(self, notification_service) -> None:
        self._service = notification_service

    def on_event(self, event_type: str, payload: dict) -> None:
        if event_type != EVENT_PAYMENT_PROCESSED:
            return
        logger.info("PAYMENT_PROCESSED event for user %s", payload.get('user_id'))
        self._service.create_and_send(
            notification_type='PAYMENT',
            recipient_id=payload.get('user_id', ''),
            metadata=payload,
        )


class AlertEventHandler(EventObserver):
    """Handles system-level alerts broadcast to all relevant parties."""

    def __init__(self, notification_service) -> None:
        self._service = notification_service

    def on_event(self, event_type: str, payload: dict) -> None:
        if event_type != EVENT_ALERT:
            return
        self._service.create_and_send(
            notification_type='ALERT',
            recipient_id=payload.get('recipient_id', ''),
            metadata=payload,
        )
