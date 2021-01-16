from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from realworld.apps.profiles.models import Profile
from realworld.testing_util import parse_body

CREATE_DATA = {
    "article": {
        "title": "제목",
        "description": "개요",
        "body": "내용"
    }
}

ARTICLE_URL = '/api/articles/'


class AuthTest(APITestCase):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="stelo",
            email="rabolution@gmail.com"
        )
        cls.user.save()
        Profile.objects.create(
            user=cls.user
        )
        cls.profile = Profile.objects.all()[0]
