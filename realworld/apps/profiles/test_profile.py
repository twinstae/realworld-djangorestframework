from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView
from realworld.testing_util import REGISTER_USER_2, TestCaseWithAuth, parse_body

PROFILE_URL = f"/api/profiles/{REGISTER_USER_2['username']}"
FOLLOW_URL = PROFILE_URL + "/follow"


class ProfileTest(TestCaseWithAuth):
    client = APIClient(enforce_csrf_checks=True)
    factory = APIRequestFactory(enforce_csrf_checks=True)

    @classmethod
    def setUpTestData(cls):
        cls.create_user_1_2()

    def test_retrieve_profile_url(self):
        self.check_url(PROFILE_URL, ProfileRetrieveAPIView)

    def test_retrieve_profile_view(self):
        request = self.factory.get(PROFILE_URL)
        assert self.check_view(
            request,
            ProfileRetrieveAPIView,
            username=REGISTER_USER_2['username']
        ) == status.HTTP_200_OK

    def test_retrieve_profile(self):
        response = self.client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': False,
        }
        assert parse_body(response)["profile"] == expected

    def test_follow_url(self):
        self.check_url(FOLLOW_URL, ProfileFollowAPIView)

    def test_follow_view(self):
        request = self.factory.post(FOLLOW_URL)
        self.authenticate(request)
        assert self.check_view(
            request,
            ProfileRetrieveAPIView,
            username=REGISTER_USER_2['username']
        ) == status.HTTP_201_CREATED

    def test_unfollow_view(self):
        request = self.factory.delete(FOLLOW_URL)
        self.authenticate(request)
        assert self.check_view(
            request,
            ProfileRetrieveAPIView,
            username=REGISTER_USER_2['username']
        ) == status.HTTP_200_OK

    def test_follow_then_unfollow(self):
        follow_response = self.client.post(FOLLOW_URL)
        assert follow_response.status_code == status.HTTP_201_CREATED
        follow_expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': True,
        }
        assert parse_body(follow_response)["profile"] == follow_expected

        unfollow_response = self.client.delete(FOLLOW_URL)
        assert unfollow_response.status_code == status.HTTP_200_OK
        unfollow_expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': False,
        }
        assert parse_body(unfollow_response)["profile"] == unfollow_expected