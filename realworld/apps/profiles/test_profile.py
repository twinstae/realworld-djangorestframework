from rest_framework import status
from rest_framework.test import APIClient, APIRequestFactory

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView
from realworld.testing_util import REGISTER_USER_2, TestCaseWithAuth

PROFILE_URL = f"/api/profiles/{REGISTER_USER_2['username']}/"
FOLLOW_URL = PROFILE_URL + "follow/"


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
        self.check_view(
            request,
            ProfileRetrieveAPIView,
            status.HTTP_200_OK
        )

    def test_retrieve_profile(self):
        response = self.client.get(PROFILE_URL)
        assert response.status_code == status.HTTP_200_OK
        expected = {
            'username': "taehee",
            'bio': '',
            'image': '',
            'following': False,
        }
        self.check_response_body(
            response,
            expected,
            model_name="profile"
        )

    def test_follow_url(self):
        self.check_url(FOLLOW_URL, ProfileFollowAPIView)

    def test_follow_view(self):
        request = self.factory.post(FOLLOW_URL)
        self.authenticate(request)
        self.check_view(
            request,
            ProfileRetrieveAPIView,
            status.HTTP_201_CREATED
        )

    def test_unfollow_view(self):
        request = self.factory.delete(FOLLOW_URL)
        self.authenticate(request)
        self.check_view(
            request,
            ProfileRetrieveAPIView,
            status.HTTP_200_OK
        )

    def test_follow_then_unfollow(self):
        follow_response = self.client.post(FOLLOW_URL)
        assert follow_response.status_code == status.HTTP_201_CREATED
        follow_expected = {
            'username': "taehee",
            'bio': '',
            'image': '',
            'following': True,
        }
        self.check_response_body(
            follow_response,
            follow_expected,
            model_name="profile"
        )

        unfollow_response = self.client.delete(FOLLOW_URL)
        assert unfollow_response.status_code == status.HTTP_200_OK
        unfollow_expected = {
            'username': "taehee",
            'bio': '',
            'image': '',
            'following': False,
        }
        self.check_response_body(
            unfollow_response,
            unfollow_expected,
            model_name="profile"
        )
