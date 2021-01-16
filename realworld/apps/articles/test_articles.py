from django.urls import resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate

from realworld.apps.articles.models import Article
from realworld.apps.articles.signals import get_slug_from_title
from realworld.apps.articles.views import ArticleViewSet
from realworld.apps.authentication.models import JwtUser
from realworld.apps.authentication.test_auth import REGISTER_URL, REGISTER_DATA
from realworld.apps.profiles.models import Profile
from realworld.testing_util import parse_body

CREATE_DATA = {
    "article": {
        "title": "제목",
        "description": "개요",
        "body": "내용"
    }
}

ARTICLE_URL = '/api/articles'


class ArticleTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @classmethod
    def setUpTestData(cls):
        response = cls.client.post(
            REGISTER_URL,
            REGISTER_DATA,
            format='json'
        )
        cls.assert_201_created(response)
        user = JwtUser.objects.get_by_natural_key('rabolution@gmail.com')
        Profile.objects.create(user=user)
        cls.profile = Profile.objects.select_related('user').get(user__username='stelo')

        cls.slug_1 = get_slug_from_title('타이틀')
        cls.article_1 = ArticleTest.create_article(cls.profile, '타이틀', '디스크립션', '바디')
        cls.article_2 = ArticleTest.create_article(cls.profile, '제목1', '개요2', '내용3')

    @staticmethod
    def create_article(profile, title, description, body):
        article = Article(
            author=profile,
            title=title,
            description=description,
            body=body,
            slug=get_slug_from_title(title)
        )
        article.save()
        return article

    def test_create_article(self):
        response = self.client.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        self.assert_201_created(response)
        body = parse_body(response)
        assert body['title'] == "제목"
        assert body['description'] == "개요"
        assert body['body'] == "내용"

    def test_create_article_view(self):
        request = self.factory.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assert_201_created(response)

    @classmethod
    def assert_201_created(cls, response):
        cls.assert_status(response, status.HTTP_201_CREATED)

    def test_create_article_without_login(self):
        response = self.client.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_article_view(self):
        request = self.factory.get(ARTICLE_URL)
        view = ArticleViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assert_status_200_OK(response)

    def assert_status_200_OK(self, response):
        self.assert_status(response, status.HTTP_200_OK)

    def test_list_article(self):
        response = self.client.get(ARTICLE_URL)
        self.assert_status_200_OK(response)

    def test_list_article_url(self):
        my_view, my_args, my_kwargs = resolve(ARTICLE_URL)
        assert my_view.__name__ == 'ArticleViewSet'

    def test_retrieve_article_view(self):
        request = self.factory.get(ARTICLE_URL + '/' + self.slug_1)
        view = ArticleViewSet.as_view({'get': 'retrieve'})
        response = view(request, slug=self.slug_1)
        self.assert_status_200_OK(response)

    @staticmethod
    def assert_status(response, code):
        assert response.status_code == code, parse_body(response) or response.status_code

    def test_retrieve_article(self):
        response = self.client.get(ARTICLE_URL + '/' + self.slug_1)
        self.assert_status_200_OK(response)
        body = parse_body(response)['article']
        assert body['title'] == "타이틀"
        assert body['description'] == "디스크립션"
        assert body['body'] == "바디"

    def test_retrieve_article_url(self):
        my_view, my_args, my_kwargs = resolve(ARTICLE_URL + '/' + self.slug_1)
        assert my_view.__name__ == 'ArticleViewSet'
