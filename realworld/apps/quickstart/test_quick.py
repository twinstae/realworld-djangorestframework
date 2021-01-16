from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from realworld.apps.quickstart.models import Snippet
from realworld.testing_util import parse_body

EXPECTED = [{'code': 'foo = "bar",',
             'highlight': 'http://testserver/snippets/1/highlight/',
             'id': 1,
             'language': 'python',
             'linenos': False,
             'owner': 'stelo',
             'style': 'friendly',
             'title': '',
             'url': 'http://testserver/snippets/1/'},
            {'code': 'print("hello, world")',
             'highlight': 'http://testserver/snippets/2/highlight/',
             'id': 2,
             'language': 'python',
             'linenos': False,
             'owner': 'stelo',
             'style': 'friendly',
             'title': '',
             'url': 'http://testserver/snippets/2/'}]

CREATE_DATA = {'code': 'new idea'}

SNIPPETS_LIST = '/snippets/'
SNIPPETS_DETAIL = '/snippets/2/'


class QuickTest(APITestCase):
    client = APIClient()

    @classmethod
    def setUpTestData(cls):
        cls.user = User(
            username='stelo',
            email='rabolution@gmail.com'
        )
        cls.user.save()
        cls.snippet = Snippet(
            code=EXPECTED[0]['code'],
            owner=cls.user
        )
        cls.snippet.save()
        cls.snippet_2 = Snippet(
            code=EXPECTED[1]['code'],
            owner=cls.user
        )
        cls.snippet_2.save()

    def test_get_users_list(self):
        response = self.client.get(SNIPPETS_LIST)
        assert response.status_code == status.HTTP_200_OK

    def test_get_snippet_list_wrong_url(self):
        response = self.client.get(SNIPPETS_LIST[:-1])
        assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY

    def test_get_snippet_list(self):
        response = self.client.get(SNIPPETS_LIST)
        assert response.status_code == status.HTTP_200_OK
        assert parse_body(response)['results'] == EXPECTED

    def test_create_snippet_without_login(self):
        response = self.client.post(
            SNIPPETS_LIST,
            CREATE_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_snippet_with_login(self):
        self.client.force_login(user=self.user)
        response = self.client.post(
            SNIPPETS_LIST,
            CREATE_DATA,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        expected_create = {
            'code': 'new idea',
            'highlight': 'http://testserver/snippets/3/highlight/',
            'id': 3,
            'language': 'python',
            'linenos': False,
            'owner': 'stelo',
            'style': 'friendly',
            'title': '',
            'url': 'http://testserver/snippets/3/'
        }
        assert parse_body(response) == expected_create

    def test_update_snippet_with_login(self):
        self.client.force_login(user=self.user)
        update = {'code': "what can i do now!"}
        response = self.client.put(SNIPPETS_DETAIL,
                                   update, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert parse_body(response)['code'] == 'what can i do now!'

    def test_update_snippet_without_login(self):
        update = {'code': "what can i do now!"}
        response = self.client.put(SNIPPETS_DETAIL,
                                   update, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_snippet_with_login(self):
        self.client.force_login(user=self.user)
        response = self.client.delete(SNIPPETS_DETAIL)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_snippet_without_login(self):
        response = self.client.delete(SNIPPETS_DETAIL)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_snippet_2(self):
        response = self.client.get(SNIPPETS_DETAIL)
        content_expected = EXPECTED[1]
        assert response.status_code == status.HTTP_200_OK
        assert parse_body(response) == content_expected
