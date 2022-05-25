from django.conf import settings
from django.test import TestCase, override_settings
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import django
import os

from routes.models import Stop

os.environ['DJANGO_SETTINGS_MODULE'] = 'tram.settings'
django.setup()


@override_settings(CACHES=settings.TEST_CACHES)
class TestStop(TestCase):

    def setUp(self):
        self.stop_names = ['stop 1', 'stop 2', 'stop 3']
        self.stops = {}
        for stop_name in self.stop_names:
            stop_obj = Stop.objects.create(name=stop_name)
            self.stops[stop_name] = stop_obj

        self.admin = get_user_model().objects.create_user(
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
