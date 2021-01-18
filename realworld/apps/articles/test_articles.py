from realworld.apps.articles.views import ArticleViewSet, TagListAPIView, ArticlesFavoriteAPIView, ArticlesFeedAPIView
from realworld.testing_util import parse_body, TestCaseWithAuth, ARTICLE_2, ARTICLE_1, get_article_data

ARTICLE_URL = '/api/articles'
TAG_URL = '/api/tags/'
RETRIEVE_EXPECTED = {
    "article": {
        'body': '바디',
        'description': '디스크립션',
        'favorited': False,
        'favoritesCount': 0,
        'title': '타이틀',
        'tagList': ['react', '태그']
    }
}
CREATE_DATA = get_article_data("제목", "개요", "내용", ["태그"])
UPDATE_DATA = get_article_data("제목있음", "개요있음", "내용있음", ["태그있음"])


class ArticleDangerousTest(TestCaseWithAuth):
    def setUp(self):
        self.create_users_1_2()
        self.create_articles_1_2()
        self.SLUG_ARTICLE_URL = ARTICLE_URL + '/' + self.slug_1
        self.FAVORITE_URL = self.SLUG_ARTICLE_URL + '/favorite/'

    def tearDown(self) -> None:
        self.delete_users_1_2()

    def test_update_article_view(self):
        request = self.auth_request(
            'put', self.SLUG_ARTICLE_URL,
            UPDATE_DATA,
            format='json'
        )
        view = ArticleViewSet.as_view(actions={'put': 'update'})
        response = view(request, slug=self.slug_1)
        self.assert_200_OK(response)
        expected = UPDATE_DATA['article'].copy()
        self.check_item(response.data, expected)

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
            UPDATE_DATA.copy()
        )

    def test_article_favorite_url(self):
        self.check_url(
            self.FAVORITE_URL,
            ArticlesFavoriteAPIView
        )

    def test_article_favorite_view(self):
        request = self.auth_request('post', self.FAVORITE_URL)
        view = ArticlesFavoriteAPIView.as_view()
        response = view(
            request,
            article_slug=self.slug_1
        )
        self.assert_201_created(response)

    def test_article_favorite(self):
        self.login()
        response = self.client.post(self.FAVORITE_URL)
        self.assert_201_created(response)
        expected = RETRIEVE_EXPECTED['article'].copy()
        expected['favorited'] = True
        expected['favoritesCount'] = 1
        self.check_item(
            parse_body(response)['article'],
            expected
        )

    def test_article_favorite_without_login(self):
        response = self.client.post(self.FAVORITE_URL)
        self.assert_403_FORBIDDEN(response)

    def test_wrong_article_favorite(self):
        self.login()
        response = self.client.post(ARTICLE_URL + '/-wrong/favorite/')
        self.assert_404_NOT_FOUND(response)

    def test_article_unfavorite(self):
        self.login()
        response = self.client.post(self.FAVORITE_URL)
        self.assert_201_created(response)

        response = self.client.delete(self.FAVORITE_URL)
        self.assert_200_OK(response)
        expected = RETRIEVE_EXPECTED['article'].copy()
        self.check_item(
            parse_body(response)['article'],
            expected
        )


class ArticleTest(TestCaseWithAuth):

    @classmethod
    def setUpTestData(cls):
        cls.create_users_1_2()
        cls.create_articles_1_2()
        cls.SLUG_ARTICLE_URL = ARTICLE_URL + '/' + cls.slug_1
        cls.FAVORITE_URL = cls.SLUG_ARTICLE_URL + '/favorite/'

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
        self.check_item_body(parse_body(response), CREATE_DATA.copy())

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

    def test_list_article_by_author_taehee(self):
        response = self.client.get(ARTICLE_URL, {'author': 'taehee'})
        self.assert_200_OK(response)

        articles_body = parse_body(response)['articles']
        assert len(articles_body) == 1
        assert articles_body[0]['title'] == ARTICLE_2['title']

    def test_list_article_by_author_stelo(self):
        response = self.client.get(ARTICLE_URL, {'author': 'stelo'})
        self.assert_200_OK(response)

        articles_body = parse_body(response)['articles']
        assert len(articles_body) == 1
        assert articles_body[0]['title'] == ARTICLE_1['title']

    def test_list_article_by_tag(self):
        response = self.client.get(ARTICLE_URL, {'tag': 'react'})
        self.assert_200_OK(response)
        articles_body = parse_body(response)['articles']
        self.check_sorted_list_body(
            articles_body,
            [ARTICLE_1],  # 제목 역순
            key='title'
        )

    def test_list_article_by_favorited_by(self):
        self.login()
        response = self.client.post(self.FAVORITE_URL)
        self.assert_201_created(response)

        response = self.client.get(ARTICLE_URL, {'favorited': 'stelo'})
        self.assert_200_OK(response)
        articles_body = parse_body(response)['articles']
        self.check_sorted_list_body(
            articles_body,
            [ARTICLE_1],  # 제목 역순
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

    def test_retrieve_article_wrong_slug(self):
        response = self.client.get(self.SLUG_ARTICLE_URL+'abc')
        self.assert_404_NOT_FOUND(response)

    def test_tag_list_url(self):
        self.check_url(
            TAG_URL,
            TagListAPIView
        )

    def test_tag_list_view(self):
        request = self.factory.get(TAG_URL)
        view = TagListAPIView.as_view()
        response = view(request)
        self.assert_200_OK(response)
        assert set(response.data['tags']) == {'react', '태그', 'django', '태그4'}

    def test_tag_list(self):
        response = self.client.get(TAG_URL)
        self.assert_200_OK(response)
        assert set(parse_body(response)['tags']) == {'react', '태그', 'django', '태그4'}

    def test_article_feed_url(self):
        self.check_url(
            '/api/articles/feed/',
            ArticlesFeedAPIView
        )

    def test_article_feed_view(self):
        request = self.auth_request('get', '/api/articles/feed/')
        view = ArticlesFeedAPIView.as_view()
        response = view(request)
        self.assert_200_OK(response)

    def test_article_feed(self):
        self.login()
        response = self.client.get('/api/articles/feed/')
        self.assert_200_OK(response)
        assert len(parse_body(response)['articles']) == 0

        follow_response = self.client.post(f"/api/profiles/{self.user_2.username}/follow")
        self.assert_201_created(follow_response)

        after_response = self.client.get('/api/articles/feed/')
        self.assert_200_OK(after_response)
        articles_after = parse_body(after_response)['articles']
        assert len(articles_after) == 1
        assert articles_after[0]['title'] == self.article_2.title
