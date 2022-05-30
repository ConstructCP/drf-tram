from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from datetime import datetime, timezone

from .models import Ticket
from accounts.models import User


class TicketSerializer(serializers.ModelSerializer):
    date_format = '%Y-%m-%d %H:%M %z'

    id = serializers.IntegerField(required=False)
    owner = serializers.CharField(source='owner.username')
    validity_time = serializers.IntegerField()
    start_time = serializers.DateTimeField(required=False, format=date_format)
    end_time = serializers.DateTimeField(read_only=True, format=date_format)

    class Meta:
        model = Ticket
        fields = ['id', 'owner', 'validity_time', 'start_time', 'end_time']

    def validate_start_time(self, start_time: datetime) -> datetime:
        """ Verify start time is now or in future """
        if start_time:
            start_time = start_time.replace(second=0, microsecond=0)
            current_time = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
            if start_time < current_time:
                raise ValidationError('Ticket start time can\'t be in the past')
        return start_time

    def validate_validity_time(self, validity_time: int) -> int:
        """ Verify validity time is in allowed values """
        if validity_time not in Ticket.TicketTime:
            raise ValidationError('Ticket validity time can be 15/30/60 min, 1 day, 1 week, 1 month')
        return validity_time

    def create(self, validated_data: dict) -> Ticket:
        """ Get owner by name and save ticket """
        owner = User.objects.get(username=validated_data['owner']['username'])
        if 'start_time' not in validated_data:
            start_time = datetime.now(tz=timezone.utc).replace(second=0, microsecond=0)
        else:
            start_time = validated_data['start_time']

        ticket = Ticket.objects.create(
            owner=owner,
            start_time=start_time,
            validity_time=validated_data['validity_time']
        )
        return ticket

    def update(self, instance: Ticket, validated_data: dict) -> Ticket:
        """ Get owner by name and update ticket instance """
        owner = User.objects.get(username=validated_data['owner']['username'])
        instance.owner = owner
        instance.start_time = validated_data['start_time']
        instance.validity_time = validated_data['validity_time']
        instance.save()
        return instance
