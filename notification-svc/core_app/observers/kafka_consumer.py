import json
import logging
import threading

from django.conf import settings
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from .base_observer import EventSubject

logger = logging.getLogger(__name__)


class KafkaEventConsumer(EventSubject):
    """
    Connects to the shared Event Bus and forwards each message to registered
    EventObserver instances (Bin full, Waste collection, Payment, etc.).
    """

    def __init__(self) -> None:
        super().__init__()
        self._consumer: KafkaConsumer | None = None
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._consume, daemon=True, name='kafka-consumer')
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._consumer:
            self._consumer.close()

    def _consume(self) -> None:
        try:
            self._consumer = KafkaConsumer(
                *settings.KAFKA_TOPICS,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                group_id=settings.KAFKA_CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=True,
            )
        except NoBrokersAvailable:
            logger.error("Kafka broker unavailable at %s", settings.KAFKA_BOOTSTRAP_SERVERS)
            return

        for msg in self._consumer:
            if not self._running:
                break
            try:
                event_type = msg.value.get('type')
                payload = msg.value.get('payload', {})
                if event_type:
                    self.notify(event_type, payload)
            except Exception:
                logger.exception("Error processing Kafka message: %s", msg.value)
