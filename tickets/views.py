from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Ticket
from .serializers import TicketSerializer
from .permissions import IsOwner


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self) -> bool:
        """ Determine whether to allow user access or not """
        if self.action in ('create', 'retrieve'):
            self.permission_classes = [IsOwner | IsAdminUser]
        elif 'my_tickets' in self.request.path:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    @action(methods=['get'], detail=False)
    def my_tickets(self, request: Request) -> Response:
        """ Returns list of tickets belonging to currently logged in user """
        tickets = Ticket.objects.filter(owner=request.user)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
