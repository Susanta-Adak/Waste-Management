import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

_kafka_started = False


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_app'

    def ready(self):
        global _kafka_started
        if _kafka_started:
            return
        _kafka_started = True

        from django.conf import settings
        if not settings.KAFKA_ENABLED:
            logger.info("Kafka consumer disabled (KAFKA_ENABLED=False)")
            return

        from .observers.kafka_consumer import KafkaEventConsumer
        from .observers.event_handlers import (
            BinFullEventHandler,
            WasteCollectionEventHandler,
            PaymentEventHandler,
        )
        from .services import NotificationService

        service = NotificationService()
        consumer = KafkaEventConsumer()
        consumer.attach(BinFullEventHandler(service))
        consumer.attach(WasteCollectionEventHandler(service))
        consumer.attach(PaymentEventHandler(service))
        consumer.start()
        logger.info("Kafka consumer started, listening on topics: %s", settings.KAFKA_TOPICS)
