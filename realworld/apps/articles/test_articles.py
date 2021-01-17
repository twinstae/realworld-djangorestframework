from realworld.apps.articles.views import ArticleViewSet
from realworld.testing_util import parse_body, TestCaseWithAuth, ARTICLE_2, ARTICLE_1, get_article_data

ARTICLE_URL = '/api/articles'
RETRIEVE_EXPECTED = {
    "article": {
        'body': '바디',
        'description': '디스크립션',
        'favorited': False,
        'favoritesCount': 0,
        'title': '타이틀',
    }
}
CREATE_DATA = get_article_data("제목", "개요", "내용")
UPDATE_DATA = get_article_data("제목없음", "개요없음", "내용없음")


class ArticleTest(TestCaseWithAuth):

    @classmethod
    def setUpTestData(cls):
        cls.create_users_1_2()
        cls.create_articles_1_2()
        cls.SLUG_ARTICLE_URL = ARTICLE_URL + '/' + cls.slug_1

    def test_create_article_url(self):
        self.check_url(
            ARTICLE_URL,
            ArticleViewSet
        )

    def test_create_article_view(self):
        request = self.auth_request(
            'post',
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        view = ArticleViewSet.as_view(actions={'post': 'create'})
        response = view(request)
        self.assert_201_created(response)

    def test_create_article(self):
        self.login()
        response = self.client.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        self.assert_201_created(response)
        self.check_item_body(
            parse_body(response),
            CREATE_DATA
        )

    def test_create_article_without_login(self):
        response = self.client.post(
            ARTICLE_URL,
            CREATE_DATA,
            format='json'
        )
        self.assert_403_FORBIDDEN(response)

    def test_list_article_view(self):
        request = self.factory.get(ARTICLE_URL)
        view = ArticleViewSet.as_view(actions={'get': 'list'})
        response = view(request)
        self.assert_200_OK(response)

    def test_list_article(self):
        response = self.client.get(ARTICLE_URL)
        self.assert_200_OK(response)
        articles_body = parse_body(response)['articles']
        self.check_sorted_list_body(
            articles_body,
            [ARTICLE_2, ARTICLE_1],  # 제목 역순
            key='title'
        )

    def test_retrieve_article_url(self):
        self.check_url(self.SLUG_ARTICLE_URL, ArticleViewSet)

    def test_retrieve_article_view(self):
        request = self.factory.get(self.SLUG_ARTICLE_URL)
        view = ArticleViewSet.as_view(actions={'get': 'retrieve'})
        response = view(request, slug=self.slug_1)
        self.assert_200_OK(response)

    def test_retrieve_article(self):
        response = self.client.get(self.SLUG_ARTICLE_URL)
        self.assert_200_OK(response)
        self.check_item_body(
            parse_body(response),
            RETRIEVE_EXPECTED
        )

    def test_update_article_view(self):
        request = self.auth_request(
            'put', self.SLUG_ARTICLE_URL,
            UPDATE_DATA,
            format='json'
        )
        view = ArticleViewSet.as_view(actions={'put': 'update'})
        response = view(request, slug=self.slug_1)
        self.assert_200_OK(response)
        self.check_item(response.data, UPDATE_DATA['article'])

    def test_update_article(self):
        self.login()
        response = self.client.put(
            self.SLUG_ARTICLE_URL,
            UPDATE_DATA,
            format='json'
        )
        self.assert_200_OK(response)
        self.check_item_body(
            parse_body(response),
            UPDATE_DATA
        )
