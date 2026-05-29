from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_app'

    def ready(self):
        # Kafka consumer is intentionally NOT started here.
        # Web workers must not own long-running consumer threads — each gunicorn
        # worker is a separate forked process, so a consumer started in ready()
        # spawns one per worker, overloading the broker with duplicate consumers
        # in the same consumer-group.
        #
        # Run the consumer separately:
        #   python manage.py consume_events
        # or via the consumer-deployment.yaml in k8s-config/.
        pass
