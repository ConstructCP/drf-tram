from django.contrib.auth.models import AbstractUser, UserManager


class TramUserManager(UserManager):
    def _create_user(self, username: str, email: str, password: str, **extra_fields) -> 'User':
        """ Underlying method for creating user objects """
        if '@' in username:
            raise ValueError('"@" symbol is not allowed in username')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username: str, email: str = None, password: str = None, **extra_fields) -> 'User':
        """ Create usual user """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username: str, email: str = None, password: str = None, **extra_fields) -> 'User':
        """ Create admin user """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, **extra_fields)

    def create(self, *args, **kwargs) -> None:
        """ Stub to prevent user from calling create() method """
        raise AttributeError('Create method should not be used with User model. Use create_user instead.')


class User(AbstractUser):
    objects = TramUserManager()
