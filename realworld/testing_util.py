import io
from typing import Union

from django.http import JsonResponse, HttpResponse
from django.urls import resolve
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate

from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.test_auth import REGISTER_URL, REGISTER_DATA
from realworld.apps.profiles.models import Profile

REGISTER_DATA_2 = {
    'user': {
        'username': "taehee",
        'email': "twinstae@naver.com",
        'password': "t1e2s3t4"
    }
}
REGISTER_USER_2 = {
    'username': "taehee",
    'email': "twinstae@naver.com",
    'password': "t1e2s3t4"
}


def parse_body(
        response: Union[JsonResponse, HttpResponse],
        method='json'
):
    if method == 'json':
        return parse_json_body(response)
    return None


def parse_json_body(response):
    stream = io.BytesIO(response.content)
    result = JSONParser().parse(stream)
    return result


class TestCaseWithAuth(APITestCase):
    @staticmethod
    def check_url(url, view_name):
        my_view, my_args, my_kwargs = resolve(url)
        assert my_view.__name__ == view_name

    @staticmethod
    def check_view(request, view, status_code):
        view = view.as_view()
        response = view(request)
        assert response.status_code == status_code

    @staticmethod
    def check_response_body(response, expected, model_name=None, keys=None):
        body = parse_body(response)
        if model_name:
            body = body[model_name]
        if not keys:
            keys = expected.keys()
        for field_name in keys:
            assert body[field_name] == expected[field_name]

    @classmethod
    def create_user_1_2(cls):
        cls.user_2 = cls.create_get_user(REGISTER_DATA_2)
        cls.user_1 = cls.create_get_user(REGISTER_DATA)

    @classmethod
    def create_get_user(cls, data):
        cls.register_user(data)
        email = data['user']['email']
        user = JwtUser.objects.get_by_natural_key(email)
        Profile.objects.create(user=user)
        return user

    @classmethod
    def register_user(cls, data):
        response = cls.client.post(
            REGISTER_URL,
            data,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED

    def login(self):
        self.client.force_authenticate(
            user=self.user_1, token=self.user_1.token)

    def authenticate(self, request):
        force_authenticate(
            request,
            user=self.user_1, token=self.user_1.token)
