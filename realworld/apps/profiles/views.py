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

    def resoponse_after_serialize(self, followee, request, status_code):
        serializer = self.get_serializer(followee, request)
        return Response(serializer.data, status=status_code)


class ProfileRetrieveAPIView(ProfileAPIView):
    permission_classes = (AllowAny,)

    def retrieve(self, request, username, *args, **kwargs):
        profile = self.get_profile_or_404(username)
        return self.resoponse_after_serialize(
            profile, request,
            status.HTTP_200_OK)


class ProfileFollowAPIView(ProfileAPIView):
    permission_classes = (IsAuthenticated,)

    def response_after_strategy(
            self, request, username,
            strategy, status_code):

        follower = request.user.profile
        followee = self.get_profile_or_404(username)
        if follower.pk is followee.pk:
            raise serializers.ValidationError(CANT_FOLLOW_YOURSELF)

        strategy(follower, followee)

        return self.resoponse_after_serialize(
            followee, request,
            status_code)

    def post(self, request, username, *args, **kwargs):
        return self.response_after_strategy(
            request, username,
            lambda a, b: a.follow(b),
            status.HTTP_201_CREATED
        )

    def delete(self, request, username, *args, **kwargs):
        return self.response_after_strategy(
            request, username,
            lambda a, b: a.unfollow(b),
            status.HTTP_200_OK
        )
