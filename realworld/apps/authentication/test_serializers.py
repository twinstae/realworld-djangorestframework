from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from realworld.apps.authentication.serializers import RegistrationSerializer, LoginSerializer
from realworld.apps.authentication.test_auth import REGISTER_DATA

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
        self.register()
        user = authenticate(
            username=REGISTER_USER_DATA['email'],
            password=REGISTER_USER_DATA['password']
        )
        assert user is not None

    def test_login_serializer(self):
        self.register()
        login_serializer = LoginSerializer(
            data=REGISTER_USER_DATA
        )

        assert login_serializer.validate(data=REGISTER_USER_DATA) == REGISTER_USER_DATA

