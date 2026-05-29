import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from core_app.observers.event_handlers import (
    AlertEventHandler,
    BinFullEventHandler,
    PaymentEventHandler,
    WasteCollectionEventHandler,
)
from core_app.observers.kafka_consumer import KafkaEventConsumer
from core_app.services import NotificationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Start the Kafka event consumer. Runs in the foreground — "
        "intended to be the sole process in the consumer Deployment."
    )

    def handle(self, *args, **options) -> None:
        if not settings.KAFKA_ENABLED:
            self.stderr.write("KAFKA_ENABLED is False — nothing to do.")
            return

        service = NotificationService()

        consumer = KafkaEventConsumer()
        consumer.attach(BinFullEventHandler(service))
        consumer.attach(WasteCollectionEventHandler(service))
        consumer.attach(PaymentEventHandler(service))
        consumer.attach(AlertEventHandler(service))

        # Blocks until SIGTERM / SIGINT
        consumer.run()
