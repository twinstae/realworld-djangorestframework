from rest_framework import status

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView
from realworld.testing_util import TestCaseWithAuth, parse_body


class ProfileDangerousTest(TestCaseWithAuth):
    def setUp(self):
        self.create_users_1_2()
        self.PROFILE_URL = f"/api/profiles/{self.user_2.username}"
        self.FOLLOW_URL = f"/api/profiles/{self.user_2.username}/follow"

    def tearDown(self) -> None:
        self.delete_users_1_2()

    def test_follow_url(self):
        self.check_url(self.FOLLOW_URL, ProfileFollowAPIView)

    def test_follow_view(self):
        request = self.auth_request('post', self.FOLLOW_URL)
        view = ProfileFollowAPIView.as_view()
        response = view(request, username=self.user_2.username)
        self.assert_201_created(response)

    def test_unfollow_view(self):
        request = self.auth_request('delete', self.FOLLOW_URL)
        view = ProfileFollowAPIView.as_view()
        response = view(request, username=self.user_2.username)
        self.assert_200_OK(response)

    def test_follow_myself(self):
        self.login()
        follow_response = self.client.post(f"/api/profiles/{self.user_1.username}/follow")
        self.assert_status(follow_response, status.HTTP_400_BAD_REQUEST)

    def test_is_followed_by_if_true(self):
        self.login()
        follow_response = self.client.post(self.FOLLOW_URL)
        self.assert_201_created(follow_response)
        assert self.profile_2.is_followed_by(self.profile_1)

    def test_is_followed_by_if_false(self):
        assert not self.profile_2.is_followed_by(self.profile_1)

    def test_follow_then_unfollow(self):
        self.login()
        follow_response = self.client.post(self.FOLLOW_URL)
        self.assert_201_created(follow_response)
        assert self.get_following(follow_response)

        unfollow_response = self.client.delete(self.FOLLOW_URL)
        self.assert_200_OK(unfollow_response)
        assert not self.get_following(unfollow_response)

    @staticmethod
    def get_following(follow_response):
        return parse_body(follow_response)["profile"]['following']


class ProfileTest(TestCaseWithAuth):
    @classmethod
    def setUpTestData(cls):
        cls.create_users_1_2()
        cls.PROFILE_URL = f"/api/profiles/{cls.user_2.username}"
        cls.FOLLOW_URL = f"/api/profiles/{cls.user_2.username}/follow"

    def test_profile_str(self):
        assert self.profile_1.__str__() == 'stelo'

    def test_retrieve_profile_url(self):
        self.check_url(self.PROFILE_URL, ProfileRetrieveAPIView)

    def test_retrieve_profile_view(self):
        request = self.factory.get(self.PROFILE_URL)
        view = ProfileRetrieveAPIView.as_view()
        response = view(
            request,
            username=self.user_2.username
        )
        self.assert_200_OK(response)

    def test_retrieve_profile(self):
        response = self.client.get(self.PROFILE_URL)
        self.assert_200_OK(response)
        expected = {
            'username': "taehee",
            'bio': '',
            'image': 'https://static.productionready.io/images/smiley-cyrus.jpg',
            'following': False,
        }
        assert parse_body(response)["profile"] == expected

    def test_retrieve_wrong_profile(self):
        response = self.client.get(self.PROFILE_URL[:-3] + 'wrong')
        self.assert_404_NOT_FOUND(response)

    @staticmethod
    def get_following(follow_response):
        return parse_body(follow_response)["profile"]['following']
