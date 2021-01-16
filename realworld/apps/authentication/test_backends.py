from datetime import datetime

from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from realworld.apps.authentication.models import JwtUser

EXPECTED_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6bnVsbC"


class ArticleTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @staticmethod
    def test_get_token():
        dt = datetime(2021, 1, 16, 13, 43, 39, 452056)
        user = JwtUser(
            username='stelo',
            email='twinstae@gmail.com'
        )
        user.save()
        assert user.get_token(user.pk, dt)[:50] == EXPECTED_TOKEN[:50]

    @classmethod
    def setUpTestData(cls):
        pass
