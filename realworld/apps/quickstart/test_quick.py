import io
from typing import Union

from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.test import APITestCase, APIClient

from realworld.apps.quickstart.models import Snippet


expected = [{'code': 'foo = "bar",',
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

SNIPPETS_LIST = '/snippets/'
SNIPPETS_DETAIL = '/snippets/2/'


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
            code=expected[0]['code'],
            owner=cls.user
        )
        cls.snippet.save()
        cls.snippet_2 = Snippet(
            code=expected[1]['code'],
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
        assert parse_body(response)['results'] == expected

    def test_create_snippet_without_login(self):
        create = {'code': 'new idea'}
        response = self.client.post(SNIPPETS_LIST,
                                    create, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_snippet_with_login(self):
        self.client.force_login(user=self.user)
        create = {'code': 'new idea'}
        response = self.client.post(SNIPPETS_LIST,
                                    create, format='json')
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
        assert response.status_code == status.HTTP_201_CREATED
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
        content_expected = expected[1]
        assert response.status_code == status.HTTP_200_OK
        assert parse_body(response) == content_expected
