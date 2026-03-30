from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('users.urls_auth')),
    path('api/profile/', include('users.urls_profile')),
    path('api/contacts/', include('contacts.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/evidence/', include('evidence.urls')),
    path('api/keyword/', include('evidence.urls_keyword')),
]
