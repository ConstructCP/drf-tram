from typing import Union

from django.contrib.auth.backends import ModelBackend
from rest_framework.request import Request

from .models import User


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(
            self,
            request: Request,
            username: str = None,
            password: str = None,
            token: str = None
    ) -> Union[User, None]:
        """ Authenticate user by email/username and password """
        if '@' in username:
            kwargs = {'email': username}
        else:
            kwargs = {'username': username}

        try:
            user = User.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id: int) -> Union[User, None]:
        """ Return user by id """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
