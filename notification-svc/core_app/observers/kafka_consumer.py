import json
import logging
import signal
import time

from django.conf import settings
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable, KafkaError

from .base_observer import EventSubject

logger = logging.getLogger(__name__)

_INITIAL_BACKOFF = 2      # seconds
_MAX_BACKOFF = 60         # seconds
_BACKOFF_FACTOR = 2


class KafkaEventConsumer(EventSubject):
    """
    Blocking Kafka consumer intended to run in its own process via the
    consume_events management command (not inside gunicorn workers).

    Reconnects automatically with exponential backoff whenever the broker is
    unreachable or the connection drops.
    """

    def __init__(self) -> None:
        super().__init__()
        self._running = False

    # ── public API ────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Block the calling thread, consuming events until SIGTERM/SIGINT."""
        self._running = True
        self._register_signals()
        logger.info(
            "Kafka consumer starting | brokers=%s topics=%s group=%s",
            settings.KAFKA_BOOTSTRAP_SERVERS,
            settings.KAFKA_TOPICS,
            settings.KAFKA_CONSUMER_GROUP,
        )
        self._consume_with_retry()

    def stop(self) -> None:
        logger.info("Kafka consumer stopping…")
        self._running = False

    # ── internals ─────────────────────────────────────────────────────────────

    def _register_signals(self) -> None:
        signal.signal(signal.SIGTERM, lambda *_: self.stop())
        signal.signal(signal.SIGINT,  lambda *_: self.stop())

    def _consume_with_retry(self) -> None:
        backoff = _INITIAL_BACKOFF
        while self._running:
            consumer = self._connect(backoff)
            if consumer is None:
                break  # stop() was called while waiting

            backoff = _INITIAL_BACKOFF  # reset after successful connect
            try:
                logger.info("Kafka consumer connected — polling…")
                for msg in consumer:
                    if not self._running:
                        break
                    self._handle(msg)
            except KafkaError:
                logger.exception("Kafka connection lost — reconnecting in %ds", backoff)
            finally:
                try:
                    consumer.close()
                except Exception:
                    pass

            if self._running:
                logger.info("Reconnecting in %ds…", backoff)
                time.sleep(backoff)
                backoff = min(backoff * _BACKOFF_FACTOR, _MAX_BACKOFF)

    def _connect(self, backoff: float) -> KafkaConsumer | None:
        """Attempt to create a KafkaConsumer, retrying with backoff on failure."""
        while self._running:
            try:
                consumer = KafkaConsumer(
                    *settings.KAFKA_TOPICS,
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                    group_id=settings.KAFKA_CONSUMER_GROUP,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    # Surface connection errors quickly rather than hanging
                    request_timeout_ms=30_000,
                    connections_max_idle_ms=60_000,
                )
                return consumer
            except NoBrokersAvailable:
                logger.warning(
                    "Kafka broker not reachable at %s — retrying in %ds",
                    settings.KAFKA_BOOTSTRAP_SERVERS,
                    backoff,
                )
                time.sleep(backoff)
                backoff = min(backoff * _BACKOFF_FACTOR, _MAX_BACKOFF)
        return None

    def _handle(self, msg) -> None:
        try:
            event_type = msg.value.get('type')
            payload = msg.value.get('payload', {})
            if event_type:
                self.notify(event_type, payload)
        except Exception:
            logger.exception(
                "Failed to process message topic=%s partition=%s offset=%s",
                msg.topic, msg.partition, msg.offset,
            )
