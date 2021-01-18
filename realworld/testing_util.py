import io
from typing import Union

from django.http import JsonResponse, HttpResponse
from django.template.response import ContentNotRenderedError
from django.urls import resolve
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase, force_authenticate, APIClient, APIRequestFactory

from realworld.apps.articles.models import Article, Tag
from realworld.apps.authentication.models import JwtUser
from realworld.apps.profiles.models import Profile


def get_article_dict(title, description, body, tags):
    return {
        "title": title,
        "description": description,
        "body": body,
        "tagList": tags
    }


def get_article_data(title, description, body, tags):
    return {
        "article": get_article_dict(
            title, description, body, tags
        )
    }


REGISTER_URL = '/api/users/'
REGISTER_DATA = {
    'user': {
        'username': "stelo",
        'email': "rabolution@gmail.com",
        'password': "test1234"
    }
}
REGISTER_DATA_2 = {
    'user': {
        'username': "taehee",
        'email': "twinstae@naver.com",
        'password': "t1e2s3t4"
    }
}
ARTICLE_1 = get_article_dict('타이틀', '디스크립션', '바디', ['react', '태그'])
ARTICLE_2 = get_article_dict("제목1", "개요2", "내용3", ['django', '태그4'])


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

            if isinstance(expected_field, list):
                assert set(actual_field) == set(expected_field), f"{actual_field} != {expected_field}"
            else:
                assert actual_field == expected_field, f"{actual_field} != {expected_field}"

    def check_item_body(self, actual_body, expected_body):
        key = list(expected_body.keys())[0]
        self.check_item(actual_body[key], expected_body[key])

    def check_sorted_list_body(self, actual_body, expected_body, key):
        assert len(actual_body) == len(expected_body), f"{actual_body}"
        sorted_body = sorted(actual_body, key=lambda item: item[key])
        for actual_item, expected_item in zip(sorted_body, expected_body):
            self.check_item(actual_item, expected_item)

    def assert_201_created(self, response):
        self.assert_status(response, status.HTTP_201_CREATED)

    def assert_200_OK(self, response):
        self.assert_status(response, status.HTTP_200_OK)

    def assert_204_NO_CONENT(self, response):
        self.assert_status(response, status.HTTP_204_NO_CONTENT)

    def assert_400_BAD_REQUEST(self, response):
        self.assert_status(response, status.HTTP_400_BAD_REQUEST)

    def assert_403_FORBIDDEN(self, response):
        self.assert_status(response, status.HTTP_403_FORBIDDEN)

    def assert_404_NOT_FOUND(self, response):
        self.assert_status(response, status.HTTP_404_NOT_FOUND)

    @staticmethod
    def assert_error_detail(response, expected):
        detail = parse_body(response)['errors']['error'][0]
        assert detail == expected, detail

    @staticmethod
    def assert_status(response, code):
        try:
            error_body = parse_body(response)
        except ContentNotRenderedError:
            error_body = response.data
        except ParseError:
            error_body = f"{response.status_code} == {code}"
        assert response.status_code == code, error_body

    @classmethod
    def create_users_1_2(cls):
        cls.user_1 = cls.create_get_user(REGISTER_DATA)
        cls.user_2 = cls.create_get_user(REGISTER_DATA_2)
        cls.profile_1 = cls.user_1.profile
        cls.profile_2 = cls.user_2.profile

    @classmethod
    def delete_users_1_2(cls):
        cls.user_1.delete()
        cls.user_2.delete()

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
    def create_article(profile, title, description, body, tagList):
        article = Article(
            author=profile,
            title=title,
            description=description,
            body=body,
        )
        article.save()
        for tag in tagList:
            t = Tag(tag=tag, slug=tag.lower())
            t.save()
            article.tags.add(t)
        return article
