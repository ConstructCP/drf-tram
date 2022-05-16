from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import StopView, RouteView, StopDetailView

router = DefaultRouter()
router.register('routes', RouteView, basename='routes')

urlpatterns = [
    path('stops/', StopView.as_view(), name='stops'),
    path('stops/<slug>/', StopDetailView.as_view(), name='stop_details'),
    path('', include(router.urls))
]
