from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory, force_authenticate

from realworld.apps.articles.models import Article
from realworld.apps.articles.signals import get_slug_from_title
from realworld.apps.articles.views import ArticleViewSet
from realworld.apps.authentication.models import JwtUser
from realworld.apps.profiles.models import Profile
from realworld.testing_util import parse_body

CREATE_DATA = {
    "article": {
        "title": "제목",
        "description": "개요",
        "body": "내용"
    }
}

ARTICLE_URL = '/api/articles/'


class ArticleTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @classmethod
    def setUpTestData(cls):
        cls.user = JwtUser.objects.create_user(
            username="stelo",
            email="rabolution@gmail.com",
            password="test1234"
        )
        cls.user.save()
        Profile.objects.create(
            user=cls.user
        )
        cls.profile = Profile.objects.all()[0]

        cls.slug_1 = get_slug_from_title('타이틀')

        cls.article_1 = Article(
            author=cls.profile,
            title='타이틀',
            description='디스크립션',
            body='바디',
            slug=cls.slug_1
        )
        cls.article_1.save()

        cls.article_2 = Article(
            author=cls.profile,
            title='제목1',
            description='개요2',
            body='내용3',
            slug=get_slug_from_title('제목1')
        )
        cls.article_2.save()

    def test_create_article(self):
        self.client.force_login(user=self.user)
        response = self.client.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
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
        force_authenticate(request, user=self.user)
        view = ArticleViewSet.as_view({'post': 'create'})
        response = view(request)

        assert response.status_code == status.HTTP_201_CREATED

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
        assert response.status_code == status.HTTP_200_OK

    def test_list_article(self):
        response = self.client.get(ARTICLE_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_article_view(self):
        request = self.factory.get(ARTICLE_URL + self.slug_1)
        view = ArticleViewSet.as_view({'get': 'retrieve'})
        response = view(request, slug=self.slug_1)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_article(self):
        response = self.client.get(ARTICLE_URL + self.slug_1)
        assert response.status_code == status.HTTP_200_OK
        body = parse_body(response)['article']
        assert body['title'] == "타이틀", body
        assert body['description'] == "디스크립션"
        assert body['body'] == "바디"
