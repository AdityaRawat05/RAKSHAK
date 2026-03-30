from django.urls import path
from .views import ProfileView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile_detail'),
    path('update/', ProfileView.as_view(), name='profile_update'),
]
