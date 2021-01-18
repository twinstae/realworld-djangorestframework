from rest_framework import status

from realworld.apps.articles.models import Comment
from realworld.apps.articles.test_articles import ARTICLE_URL
from realworld.apps.articles.views import CommentsListCreateAPIView, CommentsDestroyAPIView
from realworld.testing_util import TestCaseWithAuth, parse_body

CREATE_DATA = {
    'comment': {
        'body': "i am a comment"
    }
}


class CommentTest(TestCaseWithAuth):

    @classmethod
    def setUpTestData(cls):
        cls.create_users_1_2()
        cls.create_articles_1_2()
        cls.SLUG_ARTICLE_URL = ARTICLE_URL + '/' + cls.slug_1

        cls.COMMENT_URL = cls.SLUG_ARTICLE_URL + '/comments/'
        cls.comment_1 = cls.create_comment(cls.profile_1, cls.article_1, "바디")
        cls.comment_2 = cls.create_comment(cls.profile_2, cls.article_1, "내용1")
        cls.DELETE_COMMENT_URL = cls.COMMENT_URL+'1/'
        cls.LIST_EXPECTED = [{'body': cls.comment_2.body}, {'body': cls.comment_1.body}]

    @staticmethod
    def create_comment(profile, article, body):
        comment = Comment(
            author=profile,
            article=article,
            body=body
        )
        comment.save()
        return comment

    def test_create_list_comment_url(self):
        self.check_url(
            self.COMMENT_URL,
            CommentsListCreateAPIView
        )

    def test_create_comment_view(self):
        request = self.auth_request(
            'post',
            self.COMMENT_URL,
            CREATE_DATA,
            format='json'
        )
        view = CommentsListCreateAPIView.as_view()
        response = view(
            request,
            article_slug=self.slug_1
        )
        self.assert_201_created(response)
        self.check_item(
            response.data,
            CREATE_DATA['comment']
        )

    def test_create_comment(self):
        self.login()
        response = self.request_create_comment(self.COMMENT_URL)
        self.assert_201_created(response)
        self.check_item_body(
            parse_body(response),
            CREATE_DATA
        )

    def request_create_comment(self, url):
        return self.client.post(
            url,
            CREATE_DATA,
            format='json'
        )

    def test_create_comment_wrong_article(self):
        self.login()
        response = self.request_create_comment(ARTICLE_URL + '/wrong/comments/')
        self.assert_404_NOT_FOUND(response)

    def test_create_comment_without_login(self):
        response = self.request_create_comment(self.COMMENT_URL)
        self.assert_403_FORBIDDEN(response)

    def test_list_comments_view(self):
        request = self.factory.get(self.COMMENT_URL)
        view = CommentsListCreateAPIView.as_view()
        response = view(
            request,
            article_slug=self.slug_1
        )
        self.assert_200_OK(response)
        self.check_sorted_list_body(
            response.data['results'],
            self.LIST_EXPECTED,
            key='body'
        )

    def test_list_comments(self):
        response = self.client.get(self.COMMENT_URL)
        self.assert_200_OK(response)
        self.check_sorted_list_body(
            parse_body(response)['comments'],
            self.LIST_EXPECTED,
            key='body'
        )

    def test_list_comments_wrong_article(self):
        wrong_url = ARTICLE_URL + '/wrong/comments/'
        response = self.client.get(wrong_url)
        self.assert_200_OK(response)
        assert parse_body(response) == {
            'comments': [],
            'commentsCount': 0
        }

    def test_delete_comment_url(self):
        self.check_url(
            self.DELETE_COMMENT_URL,
            CommentsDestroyAPIView
        )

    def test_delete_comment_view(self):
        request = self.auth_request('delete', self.DELETE_COMMENT_URL)
        view = CommentsDestroyAPIView.as_view()
        response = view(
            request,
            article_slug=self.slug_1,
            comment_pk=1
        )
        self.assert_204_NO_CONENT(response)

    def test_delete_comment(self):
        self.login()
        response = self.client.delete(self.DELETE_COMMENT_URL)
        self.assert_204_NO_CONENT(response)

    def test_delete_others_comment(self):
        self.login()
        response = self.client.delete(self.COMMENT_URL+'2/')
        self.assert_403_FORBIDDEN(response)

    def test_delete_comment_without_login(self):
        response = self.client.delete(self.DELETE_COMMENT_URL)
        self.assert_403_FORBIDDEN(response)

    def test_delete_comment_wrong_id(self):
        self.login()
        response = self.client.delete(self.DELETE_COMMENT_URL[:-1]+'566/')
        self.assert_404_NOT_FOUND(response)

    def test_model_str(self):
        assert self.article_1.__str__() == '타이틀'
        assert self.comment_1.__str__() == '바디'
        assert self.article_1.tags.first().__str__() in ['react', '태그']
