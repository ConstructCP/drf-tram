from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
import django
import os

from routes.models import Stop, StopConnection

os.environ['DJANGO_SETTINGS_MODULE'] = 'tram.settings'
django.setup()


class TestPermissions(TestCase):
    def setUp(self):
        self.stop1 = Stop.objects.create(name='stop 1')
        self.stop2 = Stop.objects.create(name='stop 2')
        StopConnection.objects.create(stop1=self.stop1, stop2=self.stop2)

        self.admin = get_user_model().objects.create_user(
            username='test-admin', password='test-password', email='test-admin@example.com',
            is_staff=True
        )
        self.user = get_user_model().objects.create_user(
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
