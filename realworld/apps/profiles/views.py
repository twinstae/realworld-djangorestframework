from rest_framework import status, serializers
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realworld.apps.profiles.models import Profile
from realworld.apps.profiles.renderers import ProfileJSONRenderer
from realworld.apps.profiles.serializers import ProfileSerializer
from realworld.strings import NO_USER_FOUND_WITH_USERNAME, CANT_FOLLOW_YOURSELF


class ProfileAPIView(APIView):
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    def get_profile_or_404(self, username):
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            raise NotFound(NO_USER_FOUND_WITH_USERNAME)
        return profile

    def get_serializer(self, profile, request):
        return self.serializer_class(
            profile,
            context={'request': request}
        )

    def response_profile(self, followee, request, status):
        serializer = self.get_serializer(followee, request)
        return Response(serializer.data, status=status)


class ProfileRetrieveAPIView(ProfileAPIView):
    permission_classes = (AllowAny,)

    def retrieve(self, request, username, *args, **kwargs):
        profile = self.get_profile_or_404(username)
        return self.response_profile(profile, request, status.HTTP_200_OK)


class ProfileFollowAPIView(ProfileAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, username, *args, **kwargs):
        follower, followee = self.get_follower_followee_or_404(request, username)
        follower.follow(followee)
        return self.response_profile(followee, request, status.HTTP_201_CREATED)

    def delete(self, request, username, *args, **kwargs):
        follower, followee = self.get_follower_followee_or_404(request, username)
        follower.unfollow(followee)
        return self.response_profile(followee, request, status.HTTP_200_OK)

    def get_follower_followee_or_404(self, request, username):
        follower = request.user.profile
        followee = self.get_profile_or_404(username)
        if follower.pk is followee.pk:
            raise serializers.ValidationError(CANT_FOLLOW_YOURSELF)

        return follower, followee
