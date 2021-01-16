import jwt
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from realworld import settings
from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.serializers import RegistrationSerializer, LoginSerializer
from realworld.apps.authentication.test_auth import REGISTER_DATA
from realworld.testing_util import parse_body

REGISTER_USER_DATA = {
        'username': "stelo",
        'email': "rabolution@gmail.com",
        'password': "test1234"
    }

REGISTER_URL = '/api/users/'


class AuthSerializerTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)

    def register(self):
        response = self.client.post(
            REGISTER_URL,
            REGISTER_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        return parse_body(response)

    @staticmethod
    def test_registration_serializer():
        serializer = RegistrationSerializer(
            data=REGISTER_USER_DATA
        )
        assert serializer.is_valid()
        serializer.save()

    @staticmethod
    def test_registration_serializer_too_short_password():
        register_dict = REGISTER_USER_DATA.copy()
        register_dict['password'] = 'test123'  # len 7
        serializer = RegistrationSerializer(
            data=register_dict
        )
        assert serializer.is_valid() is False

    def test_authenticate(self):
        user_data = self.register()['user']
        token = user_data['token']
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user = JwtUser.objects.get(pk=payload['id'])

        assert user is not None, user_data

    """
        user = authenticate(
            username=user_data['email'],
            password=REGISTER_USER_DATA['password']
        )

    def test_login_serializer(self):
        user_data = self.register()
        login_serializer = LoginSerializer()

        assert login_serializer.validate(data=REGISTER_USER_DATA) == user_data, user_data
    """
