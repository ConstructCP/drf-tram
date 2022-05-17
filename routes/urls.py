from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as drf_authtoken_views

from .views import StopView, RouteView, StopDetailView

router = DefaultRouter()
router.register('routes', RouteView, basename='routes')

urlpatterns = [
    path('stops/', StopView.as_view(), name='stops'),
    path('stops/<slug>/', StopDetailView.as_view(), name='stop_details'),
    path('', include(router.urls)),

    path('auth/', include('rest_framework.urls')),
    path('token-auth/', drf_authtoken_views.obtain_auth_token),
]
