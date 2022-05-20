from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.request import Request

from .serializers import UserSerializer, UserRegistrationSerializer
from .models import User


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """ Save user if request data is valid and return api token """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
            except ValueError:
                return Response
            if user:
                token = Token.objects.create(user=user)
                json_response = serializer.data
                json_response['token'] = token.key
                return Response(json_response, status.HTTP_201_CREATED)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """ Verify username/email and password are correct and return api token """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            if '@' in serializer.data['username']:
                kwargs = {'email': serializer.data['username']}
            else:
                kwargs = {'username': serializer.data['username']}
            user = User.objects.get(**kwargs)
            token = Token.objects.get(user=user)
            json_response = {
                'username': user.username,
                'email': user.email,
                'token': token.key,
            }
            return Response(json_response, status.HTTP_200_OK)

        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
