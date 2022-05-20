from typing import Dict, List, Tuple

from rest_framework import serializers

from .models import Stop, Route, RouteStop, StopConnection


class StopSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Stop
        fields = ['id', 'name', 'slug']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ['id', 'number', 'name']


class StopDetailSerializer(StopSerializer):
    routes = RouteSerializer(many=True)

    class Meta(StopSerializer.Meta):
        fields = ['id', 'name', 'slug', 'routes']


class StopInRouteSerializer(serializers.ModelSerializer):
    class Meta(StopSerializer.Meta):
        fields = ['id']


class RouteDetailSerializer(serializers.ModelSerializer):
    stops = StopSerializer(many=True)

    class Meta:
        model = Route
        fields = ['id', 'number', 'stops', 'name']


class RouteCreationSerializer(serializers.ModelSerializer):
    stops = StopInRouteSerializer(many=True)

    class Meta:
        model = Route
        fields = ['number', 'stops']

    def validate(self, data: dict) -> dict:
        """
        Data validation
        Check uniqueness of route number
        Check there are at least 2 stops, stop ids are valid and stops have connection
        """
        errors = []
        data = super().validate(data)

        if self.context['request'].method == 'POST':
            if Route.objects.filter(number=data['number']).exists():
                errors.append({'number': 'Route with this number already exists'})

        if len(self.initial_data['stops']) < 2:
            errors.append({'stops': 'Route must include at least 2 stops.'})
        else:
            is_ids_valid, stops_ids_errors = self.validate_stop_ids(self.initial_data['stops'])
            if not is_ids_valid:
                errors += stops_ids_errors
            is_connections_valid, stops_connection_errors = self.validate_stop_connections(self.initial_data['stops'])
            if not is_connections_valid:
                errors += stops_connection_errors

        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data: dict) -> Route:
        """ Create new route """
        route = Route.objects.create(number=validated_data['number'])
        self.add_stops_in_route(route, self.initial_data['stops'])
        return route

    def update(self, instance: Route, validated_data: dict) -> Route:
        """ Update existing route """
        self.instance.number = validated_data['number']
        self.instance.save()
        stops_on_route = RouteStop.objects.filter(route=self.instance)
        stops_on_route.delete()

        self.add_stops_in_route(self.instance, self.initial_data['stops'])
        return self.instance

    def add_stops_in_route(self, route: Route, stops: List[Dict]) -> None:
        """ Create RouteStop objects thus linking route and its stops """
        route_stops = []
        try:
            number_on_route = 1
            for stop in stops:
                for key, value in stop.items():
                    stop = Stop.objects.get(id=value)
                    route_stop = RouteStop.objects.create(route=route, stop=stop, number_on_route=number_on_route)
                    route_stop.save()
                    number_on_route += 1
        except Exception as e:
            route.delete()
            for route_stop in route_stops:
                route_stop.delete()
            raise e

    def validate_stop_ids(self, stops_data: dict) -> Tuple[bool, list]:
        """ Verify all stop ids provided for route are valid """
        errors = []
        for stop in stops_data:
            for key, value in stop.items():
                if key != 'id':
                    errors.append({'stops': f'Only stop ids must be included in route creation request: {stop}'})
                try:
                    Stop.objects.get(id=value)
                except Stop.DoesNotExist:
                    errors.append({'stops': f'Invalid stop id provided: {value}'})
        return len(errors) == 0, errors

    def validate_stop_connections(self, stops_data: dict) -> Tuple[bool, list]:
        """ Verify all stops provided for route are connected. Check connection each pair of stops in sequence. """
        errors = []
        for stop1, stop2 in zip(stops_data[:-1], stops_data[1:]):
            if (
                    not StopConnection.objects.filter(stop1_id=stop1['id'], stop2_id=stop2['id']).exists() and
                    not StopConnection.objects.filter(stop1_id=stop2['id'], stop2_id=stop1['id']).exists()
            ):
                errors.append({'stops': f'Stops {stop1["id"]} and {stop2["id"]} are not connected'})
        return len(errors) == 0, errors
