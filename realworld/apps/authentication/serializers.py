from django.contrib.auth import authenticate
from rest_framework import serializers

from realworld.apps.authentication.models import JwtUser
from realworld.apps.profiles.serializers import ProfileSerializer
from realworld.strings import EMAIL_IS_REQUIRED, PASSWORD_IS_REQUIRED, NO_USER_FOUND_WITH_EMAIL_PASSWORD, \
    USER_HAS_BEEN_DEACTIVATED


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )
    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = JwtUser
        fields = ['email', 'username', 'password', 'token']

    def create(self, validated_data):
        return JwtUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)
        if email is None:
            raise serializers.ValidationError(EMAIL_IS_REQUIRED)
        if password is None:
            raise serializers.ValidationError(PASSWORD_IS_REQUIRED)

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(NO_USER_FOUND_WITH_EMAIL_PASSWORD)

        if not user.is_active:
            raise serializers.ValidationError(USER_HAS_BEEN_DEACTIVATED)

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    profile = ProfileSerializer(write_only=True)

    bio = serializers.CharField(source='profile.bio', read_only=True)
    image = serializers.CharField(source='profile.image', read_only=True)

    class Meta:
        model = JwtUser
        fields = (
            'email', 'username', 'password', 'token', 'profile', 'bio',
            'image',
        )
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        profile_data = validated_data.pop('profile', {})

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)
        instance.save()

        for (key, value) in profile_data.items():
            setattr(instance.profile, key, value)
        instance.profile.save()

        return instance
