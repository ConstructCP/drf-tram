from django.db import models
from datetime import datetime, timedelta

from accounts.models import User


class Ticket(models.Model):

    class TicketTime(models.IntegerChoices):
        TICKET_15_MIN = 15
        TICKET_30_MIN = 30
        TICKET_1_HOUR = 60
        TICKET_1_DAY = 24 * 60
        TICKET_7_DAYS = 7 * 24 * 60
        TICKET_30_DAYS = 30 * 24 * 60

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    validity_time = models.IntegerField(choices=TicketTime.choices)
    start_time = models.DateTimeField()

    @property
    def end_time(self) -> datetime:
        """ Calculate ticket end time based on start time and ticket validity time """
        return self.start_time + timedelta(minutes=self.validity_time)

    def __str__(self):
        validity_time_verbal = {
            self.TicketTime.TICKET_15_MIN: '15 min',
            self.TicketTime.TICKET_30_MIN: '30 min',
            self.TicketTime.TICKET_1_HOUR: '1 h',
            self.TicketTime.TICKET_1_DAY: '1 day',
            self.TicketTime.TICKET_7_DAYS: '7 days',
            self.TicketTime.TICKET_30_DAYS: '30 days',
        }
        start_time = self.start_time.strftime('%Y-%m-%d %H:%M %z')
        return f'{self.owner} / {validity_time_verbal[self.validity_time]} from {start_time}'
