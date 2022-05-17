from django.test import TestCase
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import django
import os

from routes.models import Stop, StopConnection, Route, RouteStop

os.environ['DJANGO_SETTINGS_MODULE'] = 'tram.settings'
django.setup()


class TestStop(TestCase):
    def setUp(self):
        self.stop_names = ['stop 1', 'stop 2', 'stop 3']
        self.stops = {}
        for stop_name in self.stop_names:
            stop_obj = Stop.objects.create(name=stop_name)
            self.stops[stop_name] = stop_obj

        self.admin = get_user_model().objects.create(
            username='test-admin', password='test-password', email='test-admin@example.com',
            is_staff=True,
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

    def test_get_all_stops(self):
        response = self.client.get('/api/v1/tram/stops/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), len(self.stops))

        for response_stop in response_data:
            db_stop = Stop.objects.get(name=response_stop['name'])
            self.assertEqual(db_stop.id, response_stop['id'])
            self.assertEqual(db_stop.slug, response_stop['slug'])

    def test_get_one_stop(self):
        stop_name = self.stop_names[0]
        stop_slug = self.stops[stop_name].slug
        response = self.client.get(f'/api/v1/tram/stops/{stop_slug}/')
        self.assertEqual(response.status_code, 200)
        response_stop = response.json()
        db_stop = Stop.objects.get(name=stop_name)

        self.assertEqual(db_stop.id, response_stop['id'])
        self.assertEqual(db_stop.name, response_stop['name'])
        self.assertEqual(db_stop.slug, response_stop['slug'])

    def test_create_stop(self):
        stop_data = {'name': 'stop create'}
        response = self.client.post('/api/v1/tram/stops/', data=stop_data)
        self.assertEqual(response.status_code, 201)

        stop_from_db = Stop.objects.get(name=stop_data['name'])
        self.assertEqual(stop_from_db.name, stop_data['name'])
        self.assertEqual(stop_from_db.slug, slugify(stop_data['name']))

    def test_update_stop(self):
        stop_name = 'stop update'
        stop = Stop.objects.create(name=stop_name)

        updated_data = {'name': 'stop update modified'}
        response = self.client.put(f'/api/v1/tram/stops/{stop.slug}/', data=updated_data)
        self.assertEqual(response.status_code, 200)
        updated_stop = Stop.objects.get(name=updated_data['name'])
        self.assertEqual(updated_stop.id, stop.id)

    def test_delete_stop(self):
        stop_name = 'stop delete'
        stop = Stop.objects.create(name=stop_name)

        response = self.client.delete(f'/api/v1/tram/stops/{stop.slug}/')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(stop, Stop.objects.all())


class TestRoute(TestCase):

    def setUp(self):
        self.stop1 = Stop.objects.create(name='stop 1')
        self.stop2 = Stop.objects.create(name='stop 2')
        self.stop3 = Stop.objects.create(name='stop 3')

        StopConnection.objects.create(stop1=self.stop1, stop2=self.stop2)
        StopConnection.objects.create(stop1=self.stop2, stop2=self.stop3)

        self.route1 = Route.objects.create(number=1)
        self.route2 = Route.objects.create(number=2)
        RouteStop.objects.bulk_create([
            RouteStop(route=self.route1, stop=self.stop1, number_on_route=1),
            RouteStop(route=self.route1, stop=self.stop2, number_on_route=2),
            RouteStop(route=self.route2, stop=self.stop2, number_on_route=1),
            RouteStop(route=self.route2, stop=self.stop3, number_on_route=2),
        ])

        self.admin = get_user_model().objects.create(
            username='test-admin', password='test-password', email='test-admin@example.com',
            is_staff=True,
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

    def test_get_route_list(self):
        response = self.client.get('/api/v1/tram/routes/')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(len(response_data), 2)

        for route_response in response_data:
            route_db = Route.objects.get(number=route_response['number'])
            self.assertEqual(route_db.id, route_response['id'])
            self.assertEqual(route_db.name, route_response['name'])

    def test_get_route_details(self):
        response = self.client.get(f'/api/v1/tram/routes/{self.route2.number}/')
        self.assertEqual(response.status_code, 200)
        route_response = response.json()
        route_db = Route.objects.get(number=self.route2.number)

        self.assertEqual(route_db.id, route_response['id'])
        self.assertEqual(route_db.number, route_response['number'])
        self.assertEqual(route_db.name, route_response['name'])
        for stop in route_response['stops']:
            stop_db = Stop.objects.get(id=stop['id'])
            self.assertEqual(stop_db.name, stop['name'])
            self.assertEqual(stop_db.slug, stop['slug'])

    def test_create_route(self):
        route_data = {
            'number': 10,
            'stops': [
                {'id': self.stop1.id},
                {'id': self.stop2.id},
            ]
        }
        response = self.client.post('/api/v1/tram/routes/', data=route_data, format='json')
        self.assertEqual(response.status_code, 201)

        route_db = Route.objects.get(number=route_data['number'])
        self.assertEqual(route_db.number, route_data['number'])

        route_stops = Stop.objects.filter(route__id=1).order_by('routestop__number_on_route')
        for stop_request, stop_db in zip(route_data['stops'], route_stops):
            self.assertEqual(stop_request['id'], stop_db.id)

    def test_route_update(self):
        route = Route.objects.create(number=20)
        RouteStop.objects.create(route=route, stop=self.stop1, number_on_route=1)
        RouteStop.objects.create(route=route, stop=self.stop2, number_on_route=2)

        route_updated_data = {
            'number': 21,
            'stops': [
                {'id': self.stop2.id},
                {'id': self.stop3.id},
            ]
        }
        response = self.client.put(f'/api/v1/tram/routes/{route.number}/', data=route_updated_data, format='json')
        self.assertEqual(response.status_code, 200)

        route_updated = Route.objects.get(id=route.id)
        self.assertEqual(route_updated.number, route_updated_data['number'])

        stops_updated = Stop.objects.filter(route=route_updated)
        self.assertNotIn(self.stop1, stops_updated)
        self.assertIn(self.stop2, stops_updated)
        self.assertIn(self.stop3, stops_updated)

    def test_route_delete(self):
        route = Route.objects.create(number=30)
        response = self.client.delete(f'/api/v1/tram/routes/{route.number}/')
        self.assertEqual(response.status_code, 204)
        self.assertNotIn(route, Route.objects.all())

    def test_route_naming(self):
        expected_name = f'{self.stop1.name} - {self.stop2.name}'
        self.assertEqual(expected_name, self.route1.name)

    def test_route_without_stops(self):
        route_data = {
            'number': 40,
            'stops': []
        }
        response = self.client.post('/api/v1/tram/routes/', data=route_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_route_with_no_connection_of_stops(self):
        route_data = {
            'number': 50,
            'stops': [
                {'id': self.stop1.id},
                {'id': self.stop3.id},
            ]
        }
        response = self.client.post('/api/v1/tram/routes/', data=route_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_list_routes_on_stop(self):
        stop1 = self.client.get(f'/api/v1/tram/stops/{self.stop1.slug}/')
        stop2 = self.client.get(f'/api/v1/tram/stops/{self.stop2.slug}/')
        stop3 = self.client.get(f'/api/v1/tram/stops/{self.stop3.slug}/')

        routes_stop1 = [r['id'] for r in stop1.json()['routes']]
        routes_stop2 = [r['id'] for r in stop2.json()['routes']]
        routes_stop3 = [r['id'] for r in stop3.json()['routes']]

        self.assertEqual(routes_stop1, [self.route1.id])
        self.assertEqual(routes_stop2, [self.route1.id, self.route2.id])
        self.assertEqual(routes_stop3, [self.route2.id])


class TestPermissions(TestCase):
    def setUp(self):
        self.stop1 = Stop.objects.create(name='stop 1')
        self.stop2 = Stop.objects.create(name='stop 2')
        StopConnection.objects.create(stop1=self.stop1, stop2=self.stop2)

        self.admin = get_user_model().objects.create(
            username='test-admin', password='test-password', email='test-admin@example.com',
            is_staff=True
        )
        self.user = get_user_model().objects.create(
            username='test-user', password='test-password', email='test-user@example.com'
        )
        self.admin_token = Token.objects.create(user=self.admin)
        self.user_token = Token.objects.create(user=self.user)

        self.admin_client = APIClient()
        self.user_client = APIClient()
        self.unauthenticated_client = APIClient()

        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        self.user_client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)

    def test_stops_get(self):
        unauth_response = self.unauthenticated_client.get('/api/v1/tram/stops/')
        self.assertEqual(unauth_response.status_code, 200)

        user_response = self.user_client.get('/api/v1/tram/stops/')
        self.assertEqual(user_response.status_code, 200)

        admin_response = self.admin_client.get('/api/v1/tram/stops/')
        self.assertEqual(admin_response.status_code, 200)

    def test_stops_post(self):
        request_data = {'name': 'permission test stop'}

        unauth_response = self.unauthenticated_client.post('/api/v1/tram/stops/', data=request_data, format='json')
        self.assertEqual(unauth_response.status_code, 401)

        user_response = self.user_client.post('/api/v1/tram/stops/', data=request_data, format='json')
        self.assertEqual(user_response.status_code, 403)

        admin_response = self.admin_client.post('/api/v1/tram/stops/', data=request_data, format='json')
        self.assertEqual(admin_response.status_code, 201)

    def test_routes_get(self):
        unauth_response = self.unauthenticated_client.get('/api/v1/tram/routes/')
        self.assertEqual(unauth_response.status_code, 200)

        user_response = self.user_client.get('/api/v1/tram/routes/')
        self.assertEqual(user_response.status_code, 200)

        admin_response = self.admin_client.get('/api/v1/tram/routes/')
        self.assertEqual(admin_response.status_code, 200)

    def test_routes_post(self):
        request_data = {
            'number': 10,
            'stops': [
                {'id': self.stop1.id},
                {'id': self.stop2.id},
            ]
        }

        unauth_response = self.unauthenticated_client.post('/api/v1/tram/routes/', data=request_data, format='json')
        self.assertEqual(unauth_response.status_code, 401)

        user_response = self.user_client.post('/api/v1/tram/routes/', data=request_data, format='json')
        self.assertEqual(user_response.status_code, 403)

        admin_response = self.admin_client.post('/api/v1/tram/routes/', data=request_data, format='json')
        self.assertEqual(admin_response.status_code, 201)
