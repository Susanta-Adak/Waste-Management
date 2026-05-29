from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, NotificationPreference, NotificationTemplate
from .serializers import (
    NotificationPreferenceSerializer,
    NotificationSerializer,
    NotificationTemplateSerializer,
    SendNotificationSerializer,
)
from .services import NotificationService


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    list:   GET /notifications/
    retrieve: GET /notifications/{id}/
    send:   POST /notifications/send/
    retry:  POST /notifications/{id}/retry/
    """

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['recipient_id', 'status', 'notification_type', 'channel']

    @action(detail=False, methods=['post'], url_path='send')
    def send(self, request):
        serializer = SendNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = NotificationService()
        notifications = service.create_and_send(**serializer.validated_data)
        return Response(
            NotificationSerializer(notifications, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'], url_path='retry')
    def retry(self, request, pk=None):
        notification = self.get_object()
        service = NotificationService()
        service._strategy.execute(notification)
        return Response(NotificationSerializer(notification).data)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """CRUD for per-user notification preferences."""

    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_id', 'notification_type', 'channel', 'is_enabled']


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """CRUD for notification message templates (admin use)."""

    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'channel', 'is_active']
