from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet
from collections import namedtuple

from .models import Stop, StopConnection, Route, RouteStop
from .serializers import StopSerializer, RouteSerializer, StopDetailSerializer, RouteDetailSerializer


class StopView(APIView):
    def get(self, request):
        stops = Stop.objects.all()
        serializer = StopSerializer(stops, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StopSerializer(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StopDetailView(ViewSet):
    def retrieve(self, request, slug):
        stop = Stop.objects.get(slug=slug)
        routes_on_stop = Route.objects.filter(stops=stop)
        setattr(stop, 'routes', routes_on_stop)
        serializer = StopDetailSerializer(stop)
        return Response(serializer.data)


class RouteView(APIView):
    def get(self, request):
        routes = Route.objects.all()
        serializer = RouteSerializer(routes, many=True)
        return Response(data=serializer.data)


class RouteDetailView(APIView):
    def get(self, request, number):
        route = Route.objects.get(number=number)
        serializer = RouteDetailSerializer(route)
        return Response(data=serializer.data)
