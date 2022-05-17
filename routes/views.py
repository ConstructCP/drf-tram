from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets, serializers
from rest_framework import generics

from .models import Stop, Route
from .serializers import StopSerializer, RouteSerializer, \
    StopDetailSerializer, RouteDetailSerializer, RouteCreationSerializer
from .permissions import ReadAnyoneWriteAdmin


class StopView(generics.ListCreateAPIView):
    queryset = Stop.objects.all()
    serializer_class = StopSerializer
    permission_classes = [ReadAnyoneWriteAdmin]


class StopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Stop.objects.all()
    lookup_field = 'slug'
    permission_classes = [ReadAnyoneWriteAdmin]

    def get_serializer_class(self) -> serializers.Serializer:
        """ Return regular serializer for GET request and detailed serializer for other requests """
        if self.request.method == 'GET':
            return StopDetailSerializer
        return StopSerializer

    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """ Get stop object with routes on this stop """
        stop = Stop.objects.get(slug=self.kwargs['slug'])
        routes_on_stop = Route.objects.filter(stops=stop)
        setattr(stop, 'routes', routes_on_stop)
        serializer = StopDetailSerializer(stop)
        return Response(serializer.data)


class RouteView(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    lookup_field = 'number'
    permission_classes = [ReadAnyoneWriteAdmin]

    def get_serializer_class(self) -> serializers.Serializer:
        """ Return right serializer basing on request type """
        if self.action == 'list':
            return RouteSerializer
        elif self.action in ('create', 'update'):
            return RouteCreationSerializer
        return RouteDetailSerializer
