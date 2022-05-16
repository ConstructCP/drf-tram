from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import generics

from .models import Stop, Route
from .serializers import StopSerializer, RouteSerializer, \
    StopDetailSerializer, RouteDetailSerializer, RouteCreationSerializer


class StopView(generics.ListCreateAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer


class StopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stop.objects.all()
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return StopDetailSerializer
        return StopSerializer

    def retrieve(self, request, *args, **kwargs):
        stop = Stop.objects.get(slug=self.kwargs['slug'])
        routes_on_stop = Route.objects.filter(stops=stop)
        setattr(stop, 'routes', routes_on_stop)
        serializer = StopDetailSerializer(stop)
        return Response(serializer.data)


class RouteView(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    lookup_field = 'number'

    def get_serializer_class(self):
        if self.action == 'list':
            return RouteSerializer
        elif self.action in ('create', 'update'):
            return RouteCreationSerializer
        return RouteDetailSerializer
