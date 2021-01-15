import io
from typing import Union

from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase, APIClient

from realworld.apps.quickstart.models import Snippet
from realworld.apps.quickstart.serializers import SnippetSerializer

expected = [
    {
        "id": 1,
        "title": "",
        "code": "foo = \"bar\"\n",
        "linenos": False,
        "language": "python",
        "style": "friendly"
    },
    {
        "id": 2,
        "title": "",
        "code": "print(\"hello, world\")\n",
        "linenos": False,
        "language": "python",
        "style": "friendly"
    }
]


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
        cls.snippet = Snippet(code=expected[0]['code'])
        cls.snippet.save()
        cls.snippet_2 = Snippet(code=expected[1]['code'])
        cls.snippet_2.save()

    def test_snippet_serialirer(self):
        serializer = SnippetSerializer(self.snippet)
        assert serializer.data == expected[0]

        content = JSONRenderer().render(serializer.data)
        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)

        serializer = SnippetSerializer(data=data)
        assert serializer.is_valid()

    def test_get_users_list(self):
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_snippet_list_wrong_url(self):
        response = self.client.get('/snippets')
        assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY

    def test_get_snippet_list(self):
        response = self.client.get('/snippets/')
        assert response.status_code == status.HTTP_200_OK
        assert parse_body(response)['results'] == expected

    def test_create_snippet(self):
        create = {
                'code': 'new idea',
                'language': 'dart'
            }
        expected_create = {
            'code': 'new idea',
            'id': 3,
            'language': 'dart',
            'linenos': False,
            'style': 'friendly',
            'title': ''
        }
        response = self.client.post(
            '/snippets/',
            create,
            format='json'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert parse_body(response) == expected_create

    def test_update_snippet(self):
        update = {
            'code': "what can i do now!",
            'linenos': True
        }
        response = self.client.put(
            '/snippets/1',
            update,
            format='json'
        )
        check_status_content(
            response,
            status.HTTP_200_OK,
            {'code': 'what can i do now!',
             'id': 1,
             'language': 'python',
             'linenos': True,
             'style': 'friendly',
             'title': ''}
        )

    def test_delete_snippet(self):

        response = self.client.delete(
            '/snippets/1'
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_get_snippet_2(self):
        response = self.client.get('/snippets/2')
        check_status_content(
            response,
            status.HTTP_200_OK,
            expected[1]
        )


def check_status_content(response, status_expected, content_expected):
    assert response.status_code == status_expected
    assert parse_body(response) == content_expected
