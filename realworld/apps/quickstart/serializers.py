from django.contrib.auth.models import User, Group
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer, IntegerField, CharField, BooleanField
from rest_framework.serializers import ChoiceField

from realworld.apps.quickstart.models import LANGUAGE_CHOICES, STYLE_CHOICES, Snippet


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SnippetSerializer(Serializer):
    id = IntegerField(
        read_only=True)
    title = CharField(
        required=False, allow_blank=True, max_length=100)
    code = CharField(
        style={'base_template': 'textarea.html'})
    linenos = BooleanField(
        required=False)
    language = ChoiceField(
        choices=LANGUAGE_CHOICES, default='python')
    style = ChoiceField(
        choices=STYLE_CHOICES, default='friendly')

    def create(self, validated_data):
        return Snippet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.code = validated_data.get('code', instance.code)
        instance.lineos = validated_data.get('lineos', instance.lineos)
        instance.language = validated_data.get('language', instance.language)
        instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
