import io
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.test import APITestCase, APIClient

from realworld.apps.quickstart.models import Snippet
from realworld.apps.quickstart.serializers import SnippetSerializer
from realworld.secret import ADMIN_PASSWORD

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

expected_json = b'{"id": 2, "title": "", "code": "print(\\"hello, world\\")\\n", "linenos": false, "language": ' \
                b'"python", "style": "friendly"} '


class QuickTest(APITestCase):
    client = APIClient()

    @classmethod
    def setUp(cls):
        cls.client.login(
            username='admin',
            password=ADMIN_PASSWORD,
        )

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
        assert content == expected_json

        stream = io.BytesIO(content)
        data = JSONParser().parse(stream)
        serializer = SnippetSerializer(data=data)
        assert serializer.is_valid()

    def test_get_users_list(self):
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_snippet_list(self):
        response = self.client.get('/snippets/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected

    def test_get_snippet_2(self):
        response = self.client.get('/snippets/2')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected[1]
