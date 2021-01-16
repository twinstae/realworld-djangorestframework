from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.views import RegistrationAPIView
from realworld.apps.profiles.models import Profile
from realworld.testing_util import parse_body

REGISTER_URL = '/api/users/'
REGISTER_DATA = {
    'user': {
        'username': "stelo",
        'email': "rabolution@gmail.com",
        'password': "test1234"
    }
}


class AuthTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    def test_register_view(self):
        request = self.factory.post(
            REGISTER_URL,
            REGISTER_DATA,
            format='json'
        )

        view = RegistrationAPIView().as_view()
        response = view(request)
        assert response.status_code == status.HTTP_201_CREATED

    def test_register(self):
        response = self.client.post(
            REGISTER_URL,
            REGISTER_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_url(self):
        my_view, my_args, my_kwargs = resolve(REGISTER_URL)
        assert my_view.__name__ == 'RegistrationAPIView'
