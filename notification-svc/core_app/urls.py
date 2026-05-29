from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet, NotificationTemplateViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('preferences', NotificationPreferenceViewSet, basename='preference')
router.register('templates', NotificationTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
