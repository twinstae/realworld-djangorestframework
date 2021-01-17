import io
from typing import Union

from django.http import JsonResponse, HttpResponse
from django.template.response import ContentNotRenderedError
from django.urls import resolve
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase, force_authenticate, APIClient, APIRequestFactory

from realworld.apps.articles.models import Article
from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.test_auth import REGISTER_URL, REGISTER_DATA
from realworld.apps.profiles.models import Profile


def get_article_dict(title, description, body):
    return {
        "title": title,
        "description": description,
        "body": body
    }


def get_article_data(title, description, body):
    return {
        "article": get_article_dict(
            title, description, body
        )
    }


ARTICLE_1 = get_article_dict('타이틀', '디스크립션', '바디')
ARTICLE_2 = get_article_dict("제목1", "개요2", "내용3")

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
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)
    user_1 = None
    user_2 = None
    profile_1 = None
    profile_2 = None
    article_1 = None
    article_2 = None
    slug_1 = None
    SLUG_ARTICLE_URL = None

    @staticmethod
    def check_url(url, view):
        my_view, my_args, my_kwargs = resolve(url)
        assert my_view.__name__ == view.__name__

    @staticmethod
    def check_item(actual_item, expected_item):
        for field_name in expected_item.keys():
            actual_field = actual_item[field_name]
            expected_field = expected_item[field_name]
            assert actual_field == expected_field, f"{actual_field} != {expected_field}"

    def check_item_body(self, actual_body, expected_body):
        key = list(expected_body.keys())[0]
        self.check_item(actual_body[key], expected_body[key])

    def check_sorted_list_body(self, actual_body, expected_body, key):
        sorted_body = sorted(actual_body, key=lambda item: item[key])
        for actual_item, expected_item in zip(sorted_body, expected_body):
            self.check_item(actual_item, expected_item)

    @classmethod
    def assert_201_created(cls, response):
        cls.assert_status(response, status.HTTP_201_CREATED)

    def assert_200_OK(self, response):
        self.assert_status(response, status.HTTP_200_OK)

    @staticmethod
    def assert_status(response, code):
        try:
            error_body = parse_body(response)
        except ContentNotRenderedError:
            message = f"""
            {response.status_code} != {code}
            """
            error_body = message
        assert response.status_code == code, error_body

    @classmethod
    def create_users_1_2(cls):
        cls.user_1 = cls.create_get_user(REGISTER_DATA)
        cls.user_2 = cls.create_get_user(REGISTER_DATA_2)
        cls.profile_1 = cls.user_1.profile
        cls.profile_2 = cls.user_2.profile

    @classmethod
    def create_articles_1_2(cls):
        cls.article_1 = cls.create_article(
            cls.profile_1, **ARTICLE_1
        )
        cls.article_2 = cls.create_article(
            cls.profile_2, **ARTICLE_2
        )
        cls.slug_1 = cls.article_1.slug

    @staticmethod
    def create_article(profile, title, description, body):
        article = Article(
            author=profile,
            title=title,
            description=description,
            body=body
        )
        article.save()
        return article

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

    def auth_request(self, http, url, data=None, **kwargs):
        request = self.factory.__getattribute__(http)(url, data, **kwargs)
        self.authenticate(request)
        return request
