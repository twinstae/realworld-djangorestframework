from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from realworld.apps.authentication.views import RegistrationAPIView, UserRetrieveUpdateAPIView, LoginAPIView
from realworld.testing_util import TestCaseWithAuth, parse_body, REGISTER_DATA, REGISTER_URL, REGISTER_DATA_2

UPDATE_DATA = {
    'user': {
        'username': "twinstae",
        'email': "twinstae@gmail.com",
        'password': "1234test",
        'bio': "Are you ready to make the world more better place?"
    }
}


class AuthTest(TestCaseWithAuth):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = cls.create_get_user(REGISTER_DATA)
        cls.UPDATE_URL = REGISTER_URL+f'{cls.user_1.pk}/'
        cls.LOGIN_URL = REGISTER_URL + 'login/'

    def test_register_url(self):
        self.check_url(REGISTER_URL, RegistrationAPIView)

    def test_register_view(self):
        request = self.factory.post(
            REGISTER_URL,
            REGISTER_DATA_2,
            format='json'
        )
        view = RegistrationAPIView().as_view()
        response = view(request)
        self.assert_201_created(response)

    def test_register(self):
        response = self.client.post(
            REGISTER_URL,
            REGISTER_DATA_2,
            format='json'
        )
        self.assert_201_created(response)
        assert 'token' in parse_body(response)['user']

    def test_login_url(self):
        self.check_url(
            self.LOGIN_URL,
            LoginAPIView
        )

    def test_auth(self):
        user = REGISTER_DATA['user']
        auth_user = authenticate(username=user['email'], password=user['password'])
        assert auth_user is not None

    def test_login_view(self):
        request = self.factory.post(
            self.LOGIN_URL,
            REGISTER_DATA,
            format='json'
        )
        view = LoginAPIView.as_view()
        response = view(request)
        self.assert_200_OK(response)
        assert 'token' in response.data

    def test_login(self):
        response = self.client.post(
            self.LOGIN_URL,
            REGISTER_DATA,
            format='json'
        )
        self.assert_200_OK(response)
        assert 'token' in parse_body(response)['user']

    def test_retrieve_update_url(self):
        self.check_url(
            self.UPDATE_URL,
            UserRetrieveUpdateAPIView
        )

    def test_retrieve_view(self):
        request = self.auth_request(
            'get', self.UPDATE_URL
        )
        view = UserRetrieveUpdateAPIView().as_view()
        response = view(request)
        self.assert_200_OK(response)
        expected = REGISTER_DATA['user'].copy()
        del expected['password']
        self.check_item(
            response.data,
            expected
        )

    def test_retrieve(self):
        self.login()
        response = self.client.get(self.UPDATE_URL)
        self.assert_200_OK(response)
        expected = REGISTER_DATA['user'].copy()
        del expected['password']
        self.check_item(
            parse_body(response)['user'],
            expected
        )

    def test_update_view(self):
        request = self.auth_request(
            'put', self.UPDATE_URL,
            UPDATE_DATA,
            format='json'
        )
        view = UserRetrieveUpdateAPIView().as_view()
        response = view(request)
        self.assert_200_OK(response)

    def test_update(self):
        request = self.auth_request(
            'put', self.UPDATE_URL,
            UPDATE_DATA,
            format='json'
        )
        view = UserRetrieveUpdateAPIView().as_view()
        response = view(request)
        assert response.status_code == status.HTTP_200_OK