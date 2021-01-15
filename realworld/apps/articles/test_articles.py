import io
from typing import Union

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.test import TestCase

# Create your tests here.
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase, APIClient

from realworld.apps.articles.models import Article
from realworld.apps.profiles.models import Profile


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


class ArticleTest(APITestCase):
    client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.user = User(
            username="stelo",
            email="rabolution@gmail.com"
        )
        cls.profile = Profile(user=cls.user)

        cls.article_1 = Article(
            author=cls.profile,
            title='타이틀',
            description='디스크립션',
            body='바디',
        )
        cls.article_2 = Article(
            author=cls.profile,
            title='제목1',
            description='개요2',
            body='내용3',
        )

    def test_create_article(self):
        self.client.force_login(user=self.user)
        response = self.client.post(
            'api/articles',
            {
                "article": {
                    "title": "제목",
                    "description": "개요",
                    "body": "내용"
                }
            },
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        body = parse_body(response)
        assert body['title'] == "제목"
        assert body['description'] == "개요"
        assert body['body'] == "내용"

    def test_create_article_without_login(self):
        response = self.client.post(
            'api/articles',
            {
                "article": {
                    "title": "제목",
                    "description": "개요",
                    "body": "내용"
                }
            },
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
