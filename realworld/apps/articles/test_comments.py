from realworld.apps.articles.models import Comment
from realworld.apps.articles.test_articles import ARTICLE_URL
from realworld.apps.articles.views import CommentsListCreateAPIView
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
        cls.comment_2 = cls.create_comment(cls.profile_1, cls.article_1, "내용1")
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

    def test_create_comment(self):
        self.login()
        response = self.client.post(
            self.COMMENT_URL,
            CREATE_DATA,
            format='json'
        )
        self.assert_201_created(response)
        self.check_item_body(
            parse_body(response),
            CREATE_DATA
        )

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
