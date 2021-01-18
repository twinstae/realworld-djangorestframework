import pytest
from django.contrib.auth import authenticate
from django.contrib.auth.backends import ModelBackend
from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from realworld.apps.authentication.models import UserManager, JwtUser
from realworld.apps.authentication.views import RegistrationAPIView, UserRetrieveUpdateAPIView, LoginAPIView
from realworld.strings import PASSWORD_IS_REQUIRED, EMAIL_IS_REQUIRED, NO_USER_FOUND_WITH_EMAIL_PASSWORD, \
    USER_HAS_BEEN_DEACTIVATED
from realworld.testing_util import TestCaseWithAuth, parse_body, REGISTER_DATA, REGISTER_URL, REGISTER_DATA_2

UPDATE_DATA = {
    'user': {
        'username': "twinstae",
        'email': "twinstae@gmail.com",
        'password': "n2wp6ssw0r4",
        'bio': "Are you ready to make the world more better place?"
    }
}


class AuthDangerousTest(TestCaseWithAuth):
    def setUp(self) -> None:
        self.user_1 = self.create_get_user(REGISTER_DATA)
        self.UPDATE_URL = REGISTER_URL+f'{self.user_1.pk}/'
        self.LOGIN_URL = REGISTER_URL + 'login/'
        self.user_manager = UserManager()

    def tearDown(self) -> None:
        self.user_1.delete()

    def test_create_user_without_name(self):
        with pytest.raises(TypeError) as excinfo:
            self.user_manager.create_user(username="", email="twinsjae@naver.com")

    def test_create_user_without_email(self):
        with pytest.raises(TypeError) as excinfo:
            self.user_manager.create_user(username="rabbit", email="")

    def test_create_superuser_without_password(self):
        with pytest.raises(TypeError) as excinfo:
            self.user_manager.create_user(
                username="jaehee",
                email="twinsjae@naver.com",
                password="test1234"
            )

    def test_user_str(self):
        assert self.user_1.__str__() == self.user_1.email

    def test_user_get_full_name(self):
        assert self.user_1.get_full_name() == self.user_1.username

    def test_user_get_short_name(self):
        assert self.user_1.get_short_name() == self.user_1.username

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

    def test_update_view(self):
        request = self.auth_request(
            'put', self.UPDATE_URL, UPDATE_DATA, format='json')
        view = UserRetrieveUpdateAPIView().as_view()
        response = view(request)
        self.assert_200_OK(response)

    def test_update(self):
        self.login()
        response = self.client.put(self.UPDATE_URL, UPDATE_DATA, format='json')
        self.assert_200_OK(response)
        self.client.force_authenticate()

        expected = UPDATE_DATA['user'].copy()
        assert self.user_1.email == expected['email']
        assert self.user_1.check_password(expected['password'])

        login_data = {
            'user': {
                'email': expected['email'],
                'password': expected['password']
            }
        }

        user = JwtUser.objects.get_by_natural_key(expected['email'])
        assert self.user_1.email == user.email
        assert user.check_password(expected['password'])

        assert authenticate(username=expected['email'], password=expected['password']) is not None

        del expected['password']
        self.check_item_body(parse_body(response), {'user': expected})

        login_response = self.login_response_with(login_data)
        self.assert_200_OK(login_response)
        assert 'token' in parse_body(login_response)['user']

    def login_response_with(self, data):
        return self.client.post(
            self.LOGIN_URL,
            data,
            format='json'
        )


class AuthTest(TestCaseWithAuth):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_1 = cls.create_get_user(REGISTER_DATA)
        cls.UPDATE_URL = REGISTER_URL + f'{cls.user_1.pk}/'
        cls.LOGIN_URL = REGISTER_URL + 'login/'
        cls.user_manager = UserManager()

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
        response = self.login_response_with(REGISTER_DATA)
        self.assert_200_OK(response)
        assert 'token' in parse_body(response)['user']

    def test_login_with_deactivated_user(self):
        self.user_1.is_active = False
        self.user_1.save()

        response = self.login_response_with(REGISTER_DATA)
        self.assert_400_BAD_REQUEST(response)
        self.assert_error_detail(response, NO_USER_FOUND_WITH_EMAIL_PASSWORD)

    def test_login_without_password(self):
        data = self.get_login_data_without('password')
        response = self.login_response_with(data)
        self.assert_400_BAD_REQUEST(response)
        assert 'password' in parse_body(response)['errors']

    def test_login_without_email(self):
        data = self.get_login_data_without('email')
        response = self.login_response_with(data)
        self.assert_400_BAD_REQUEST(response)
        assert 'email' in parse_body(response)['errors']

    def test_login_with_wrong_email(self):
        data = self.get_login_data_without('email')
        data['user']['email'] = "jaetwins@tmail.con"
        response = self.login_response_with(data)
        self.assert_400_BAD_REQUEST(response)
        self.assert_error_detail(response, NO_USER_FOUND_WITH_EMAIL_PASSWORD)

    def login_response_with(self, data):
        return self.client.post(
            self.LOGIN_URL,
            data,
            format='json'
        )

    @staticmethod
    def get_login_data_without(field_name):
        user_data = REGISTER_DATA['user'].copy()
        del user_data[field_name]
        assert field_name not in user_data
        return {'user': user_data}

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

