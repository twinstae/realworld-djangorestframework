from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from realworld.secret import ADMIN_PASSWORD


class UserTest(APITestCase):
    client = APIClient()

    @classmethod
    def setUp(cls):
        cls.client.login(
            username='admin',
            password=ADMIN_PASSWORD,
        )

    def test_get_users_list(self):
        response = self.client.get('/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
