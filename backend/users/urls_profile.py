from django.urls import path
from .views import ProfileView, UpdateLocationView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile_detail'),
    path('update/', ProfileView.as_view(), name='profile_update'),
    path('update-location/', UpdateLocationView.as_view(), name='profile_location_sync'),
]
