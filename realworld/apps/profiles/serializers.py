from rest_framework import serializers as ser

from realworld.apps.profiles.models import Profile


class ProfileSerializer(ser.ModelSerializer):
    username = ser.CharField(source='user.username')
    bio = ser.CharField(allow_blank=True, required=False)
    image = ser.SerializerMethodField()
    following = ser.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username', 'bio', 'image', 'following')
        read_only_fields = ('username',)

    @staticmethod
    def get_image(obj) -> str:
        if obj.image:
            return obj.image
        return 'https://static.productionready.io/images/smiley-cyrus.jpg'

    def get_following(self, instance: Profile) -> bool:
        request = self.context.get('request', None)
        if request is None:
            return False
        if not request.user.is_authenticated:
            return False

        follower = request.user.profile
        followee = instance
        return follower.is_following(followee)
