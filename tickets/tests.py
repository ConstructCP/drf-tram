from django.test import TestCase
from datetime import datetime, timedelta, timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import django
import os


from accounts.models import User
from .models import Ticket

os.environ['DJANGO_SETTINGS_MODULE'] = 'tram.settings'
django.setup()


class TestTickets(TestCase):
    date_format = '%Y-%m-%d %H:%M %z'

    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', 'user-password')
        self.user_token = Token.objects.create(user=self.user)
        self.user_client = APIClient()
        self.user_client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)

        self.admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin-password')
        self.admin_token = Token.objects.create(user=self.admin)
        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)

        validity_time = Ticket.TicketTime.TICKET_1_HOUR
        self.user_tickets = [
            Ticket.objects.create(owner=self.user, validity_time=validity_time,
                                  start_time=datetime.now(tz=timezone.utc)),
            Ticket.objects.create(owner=self.user, validity_time=validity_time,
                                  start_time=datetime.now(tz=timezone.utc) + timedelta(hours=12)),
        ]
        self.admin_tickets = [
            Ticket.objects.create(owner=self.admin, validity_time=validity_time,
                                  start_time=datetime.now(tz=timezone.utc)),
            Ticket.objects.create(owner=self.admin, validity_time=validity_time,
                                  start_time=datetime.now(tz=timezone.utc) + timedelta(hours=12)),
        ]
        self.all_tickets = self.admin_tickets + self.user_tickets

    def test_user_create_ticket(self):
        data = {
            'validity_time': Ticket.TicketTime.TICKET_15_MIN,
            'start_time': datetime.now(tz=timezone.utc).strftime(self.date_format),
            'owner': self.user.username,
        }
        response = self.user_client.post('/api/v1/tickets/', data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['validity_time'], data['validity_time'])
        self.assertEqual(response.data['start_time'], data['start_time'])
        self.assertEqual(response.data['owner'], self.user.username)

    def test_user_create_ticket_no_start_time(self):
        current_time = datetime.now(tz=timezone.utc)
        data = {
            'validity_time': Ticket.TicketTime.TICKET_15_MIN,
            'owner': self.user.username,
        }
        response = self.user_client.post('/api/v1/tickets/', data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['validity_time'], data['validity_time'])
        self.assertEqual(response.data['owner'], self.user.username)

        ticket_start_time = datetime.strptime(response.data['start_time'], self.date_format).now(tz=timezone.utc)
        self.assertTrue(current_time - ticket_start_time < timedelta(minutes=1))

    def test_user_get_ticket(self):
        response = self.user_client.get(f'/api/v1/tickets/{self.user_tickets[0].id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertEqual(response.data['validity_time'], self.user_tickets[0].validity_time)
        self.assertEqual(response.data['start_time'], self.user_tickets[0].start_time.strftime(self.date_format))

    def test_user_get_my_tickets(self):
        response = self.user_client.get(f'/api/v1/tickets/my_tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.user_tickets))

        response_data = list(sorted(response.data, key=lambda ticket: ticket['start_time']))
        for response_ticket, db_ticket in zip(response_data, self.user_tickets):
            self.assertEqual(response_ticket['owner'], db_ticket.owner.username)
            self.assertEqual(response_ticket['validity_time'], db_ticket.validity_time)
            self.assertEqual(response_ticket['start_time'], db_ticket.start_time.strftime(self.date_format))

    def test_admin_get_tickets(self):
        response = self.admin_client.get(f'/api/v1/tickets/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), len(self.all_tickets))

        response_data = list(sorted(response.data, key=lambda ticket: (ticket['owner'], ticket['start_time'])))
        for response_ticket, db_ticket in zip(response_data, self.all_tickets):
            self.assertEqual(response_ticket['owner'], db_ticket.owner.username)
            self.assertEqual(response_ticket['validity_time'], db_ticket.validity_time)
            self.assertEqual(response_ticket['start_time'], db_ticket.start_time.strftime(self.date_format))

    def test_admin_update_ticket(self):
        ticket = Ticket.objects.create(owner=self.user, validity_time=Ticket.TicketTime.TICKET_1_DAY,
                                       start_time=datetime.now(tz=timezone.utc))
        new_validity_time = Ticket.TicketTime.TICKET_7_DAYS
        new_start_time = datetime.now(tz=timezone.utc) + timedelta(days=7)
        updated_ticket_data = {
            'owner': self.user.username,
            'validity_time': new_validity_time,
            'start_time': new_start_time,
        }

        response = self.admin_client.put(f'/api/v1/tickets/{ticket.id}/', data=updated_ticket_data, format='json')
        self.assertEqual(response.status_code, 200)
        ticket_updated = Ticket.objects.get(id=ticket.id)
        self.assertEqual(ticket_updated.validity_time, new_validity_time)
        self.assertEqual(ticket_updated.start_time, new_start_time.replace(second=0, microsecond=0))
        self.assertEqual(ticket_updated.owner, ticket.owner)

    def test_admin_delete_ticket(self):
        ticket = Ticket.objects.create(owner=self.user, validity_time=Ticket.TicketTime.TICKET_1_DAY,
                                       start_time=datetime.now(tz=timezone.utc))
        response = self.admin_client.delete(f'/api/v1/tickets/{ticket.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(Ticket.objects.filter(id=ticket.id)), 0)

    def test_create_ticket_with_invalid_validity_time(self):
        ticket_data = {
            'owner': self.user.username,
            'validity_time': 42,
            'start_time': datetime.now(tz=timezone.utc),
        }
        response = self.admin_client.post('/api/v1/tickets/', data=ticket_data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_ticket_end_time(self):
        validity_times = {time: timedelta(minutes=time) for time in Ticket.TicketTime}
        for time, time_delta in validity_times.items():
            start_time = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
            ticket = Ticket.objects.create(owner=self.user, validity_time=time,
                                           start_time=start_time)
            response_ticket = self.admin_client.get(f'/api/v1/tickets/{ticket.id}/')
            self.assertEqual(response_ticket.data['end_time'], (start_time + time_delta).strftime(self.date_format))

    """
    user create ticket
    user create ticket without start time
    user get ticket
    user get my tickets
    admin get all tickets
    admin update ticket
    admin delete ticket
    create ticket with invalid valitity time
    check end time of tickets
    """
