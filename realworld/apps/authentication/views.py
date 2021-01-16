from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from realworld.apps.authentication.renderers import JwtUserJSONRenderer
from realworld.apps.authentication.serializers import RegistrationSerializer, LoginSerializer, UserSerializer


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JwtUserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = get_validated_user_serializer(
            request,
            self.serializer_class
        )
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (JwtUserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = get_validated_user_serializer(
            request,
            self.serializer_class
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


def get_validated_user_serializer(request, serializer_class):
    user = request.data.get('user', {})
    serializer = serializer_class(data=user)
    serializer.is_valid(raise_exception=True)
    return serializer


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JwtUserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        user_data = request.data.get('user', {})

        user = request.user
        profile = user.profile
        serializer_data = self.get_updated_data(
            user_data,
            user, profile
        )
        serializer = self.serializer_class(
            user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def get_updated_data(data, mother, child):
        def get(field_name, obj):
            return data.get(field_name, getattr(obj, field_name))

        def get_update(obj):
            fields = map(lambda f: f.name, obj._meta.fields)
            return {f: get(f, obj) for f in fields}

        result = get_update(mother)
        if child:
            child_name = type(child).__name__.lower()
            result[child_name] = get_update(child)
        return result
