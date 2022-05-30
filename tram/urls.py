from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/tram/', include('routes.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/v1/tickets/', include('tickets.urls')),
]
