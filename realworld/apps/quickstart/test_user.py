from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from realworld.secret import ADMIN_PASSWORD


class UserTest(APITestCase):
    client = APIClient()
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

    @classmethod
    def setUp(cls):
        cls.client.login(
            username='admin',
            password=ADMIN_PASSWORD,
        )

    @classmethod
    def setUpTestData(cls):

        snippet = Snippet(code=cls.expected[0]['code'])
        snippet.save()

        snippet = Snippet(code=cls.expected[1]['code'])
        snippet.save()

    def test_get_users_list(self):
        response = self.client.get('/users/')
        assert response.status_code == status.HTTP_200_OK

    def test_get_snippet_list(self):
        response = self.client.get('/snippets/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == self.expected

    def test_get_snippet_2(self):
        response = self.client.get('/snippets/2')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == self.expected[1]
