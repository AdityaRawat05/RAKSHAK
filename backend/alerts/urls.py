from django.urls import path
from .views import AlertTriggerView, AlertVerifyView, AlertNearbyView, AlertResolveView

urlpatterns = [
    path('trigger/', AlertTriggerView.as_view(), name='alert_trigger'),
    path('verify/', AlertVerifyView.as_view(), name='alert_verify'),
    path('nearby/', AlertNearbyView.as_view(), name='alert_nearby'),
    path('<str:alert_id>/resolve/', AlertResolveView.as_view(), name='alert_resolve'),
]
