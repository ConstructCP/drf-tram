from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class TestAccounts(TestCase):
    def setUp(self):
        self.user_password = 'test-password'
        self.user = get_user_model().objects.create_user(
            username='test-user',
            email='test-user@example.com',
            password=self.user_password,
        )
        self.user_token = Token.objects.create(user=self.user)

        self.client = APIClient()

    def test_register_user(self):
        data = {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'password',
        }

        response = self.client.post('/accounts/register/', data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['username'], data['username'])
        self.assertEqual(response.data['email'], data['email'])
        self.assertNotIn('password', response.data)

        token = Token.objects.get(user__username=data['username'])
        self.assertEqual(response.data['token'], token.key)

    def test_register_with_duplicate_email(self):
        data = {
            'username': 'test',
            'email': 'test-user@example.com',
            'password': 'password',
        }

        response = self.client.post('/accounts/register/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_without_email(self):
        data = {
            'username': 'test',
            'password': 'password',
        }

        response = self.client.post('/accounts/register/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_username(self):
        data = {
            'username': 'test@test',
            'email': 'testtest@example.com',
            'password': 'password',
        }

        response = self.client.post('/accounts/register/', data=data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_login_with_username(self):
        data = {
            'username': self.user.username,
            'password': self.user_password,
        }

        response = self.client.post('/accounts/login/', data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertNotIn('password', response.data)

        self.assertEqual(response.data['token'], self.user_token.key)

    def test_login_with_email(self):
        data = {
            'username': self.user.email,
            'password': self.user_password,
        }

        response = self.client.post('/accounts/login/', data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertNotIn('password', response.data)

        self.assertEqual(response.data['token'], self.user_token.key)
