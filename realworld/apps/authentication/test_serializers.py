from django.contrib.auth import authenticate
from rest_framework.test import APITestCase

from realworld.apps.authentication.serializers import RegistrationSerializer, LoginSerializer


REGISTER_DATA = {
            'email': 'rabolution@gmail.com',
            'username': 'stelo',
            'password': 'test1234'  # len 8
        }


class AuthSerializerTest(APITestCase):
    @staticmethod
    def test_registration_serializer():
        serializer = RegistrationSerializer(
            data=REGISTER_DATA
        )
        assert serializer.is_valid()
        serializer.save()

    @staticmethod
    def test_registration_serializer_too_short_password():
        register_dict = REGISTER_DATA.copy()
        register_dict['password'] = 'test123'  # len 7
        serializer = RegistrationSerializer(
            data=register_dict
        )
        assert serializer.is_valid() is False

    @staticmethod
    def test_authenticate():
        user = authenticate(
            username=REGISTER_DATA['email'],
            password=REGISTER_DATA['password']
        )
        assert user is not None

    @staticmethod
    def test_login_serializer():
        login_serializer = LoginSerializer(
            data=REGISTER_DATA
        )

        assert login_serializer.validate(data=REGISTER_DATA) == {
            'email': REGISTER_DATA['email'],
            'password': REGISTER_DATA['password']
        }

