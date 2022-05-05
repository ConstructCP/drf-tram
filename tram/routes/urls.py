from django.urls import path

from .views import StopView, RouteView, StopDetailView, RouteDetailView

urlpatterns = [
    path('stops/', StopView.as_view(), name='stops'),
    path('routes/', RouteView.as_view(), name='routes'),
    path('stops/<slug>/', StopDetailView.as_view({
        'get': 'retrieve'
    }), name='stop_details'),
    path('routes/<int:number>/', RouteDetailView.as_view(), name='route_details'),
]
