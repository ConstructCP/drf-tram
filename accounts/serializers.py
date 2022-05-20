from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, data: dict) -> dict:
        """ Check if username/email is valid and password is correct """
        errors = []
        data = super().validate(data)

        if '@' in data['username']:
            kwargs = {'email': data['username']}
        else:
            kwargs = {'username': data['username']}

        try:
            user = User.objects.get(**kwargs)
            if user.check_password(data['password']):
                return data
            else:
                errors.append({'password': 'Provided password is incorrect'})
        except User.DoesNotExist:
            errors.append({'username': 'User with provided username/email was not found'})

        if errors:
            raise serializers.ValidationError(errors)


class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, username: str) -> str:
        """ Verify username doesn't contain @ symbol """
        if '@' in username:
            raise serializers.ValidationError('Username can\'t contain "@" symbol.')
        return username

    def create(self, validated_data: dict) -> User:
        """ Create new user from validated data """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
