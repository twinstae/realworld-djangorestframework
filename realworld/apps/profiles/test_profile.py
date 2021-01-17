from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView
from realworld.testing_util import REGISTER_USER_2, TestCaseWithAuth, parse_body

PROFILE_URL = f"/api/profiles/{REGISTER_USER_2['username']}"
FOLLOW_URL = PROFILE_URL + "/follow"


class ProfileTest(TestCaseWithAuth):
    @classmethod
    def setUpTestData(cls):
        cls.create_users_1_2()

    def test_retrieve_profile_url(self):
        self.check_url(PROFILE_URL, ProfileRetrieveAPIView)

    def test_retrieve_profile_view(self):
        request = self.factory.get(PROFILE_URL)
        view = ProfileRetrieveAPIView.as_view()
        response = view(
            request,
            username=REGISTER_USER_2['username']
        )
        self.assert_200_OK(response)

    def test_retrieve_profile(self):
        response = self.client.get(PROFILE_URL)
        self.assert_200_OK(response)
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
        request = self.auth_request('post', FOLLOW_URL)
        view = ProfileFollowAPIView.as_view()
        response = view(request, username=REGISTER_USER_2['username'])
        self.assert_201_created(response)

    def test_unfollow_view(self):
        request = self.auth_request('delete', FOLLOW_URL)
        view = ProfileFollowAPIView.as_view()
        response = view(request, username=REGISTER_USER_2['username'])
        self.assert_200_OK(response)

    def test_follow_then_unfollow(self):
        self.login()
        follow_response = self.client.post(FOLLOW_URL)
        self.assert_201_created(follow_response)
        follow_expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': True,
        }
        assert parse_body(follow_response)["profile"] == follow_expected

        unfollow_response = self.client.delete(FOLLOW_URL)
        self.assert_200_OK(unfollow_response)
        unfollow_expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': False,
        }
        assert parse_body(unfollow_response)["profile"] == unfollow_expected
