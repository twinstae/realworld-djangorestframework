from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Profile
from .renderers import ProfileJSONRenderer
from .serializers import ProfileSerializer
from ...strings import NO_USER_FOUND_WITH_USERNAME, CANT_FOLLOW_YOURSELF


class ProfileMixIn:
    renderer_classes = (ProfileJSONRenderer,)
    serializer_class = ProfileSerializer

    @staticmethod
    def get_profile_or_404(username):
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

    def response_after_serialize(
            self,
            followee, request, status_code
    ) -> Response:
        serializer = self.get_serializer(followee, request)
        return Response(serializer.data, status=status_code)


class ProfileRetrieveAPIView(ProfileMixIn, RetrieveAPIView):
    permission_classes = (AllowAny,)
    queryset = Profile.objects.select_related('user')

    def retrieve(self, request, username, *args, **kwargs):
        profile = self.get_profile_or_404(username)
        return self.response_after_serialize(
            profile, request,
            status.HTTP_200_OK)


class ProfileFollowAPIView(ProfileMixIn, APIView):
    permission_classes = (IsAuthenticated,)

    def response_after_strategy(
            self, request, username,
            strategy, status_code):
        follower = request.user.profile
        followee = self.get_profile_or_404(username)
        if follower.pk is followee.pk:
            raise ValidationError(CANT_FOLLOW_YOURSELF)

        strategy(follower, followee)

        return self.response_after_serialize(
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
