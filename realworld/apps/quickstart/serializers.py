from django.contrib.auth.models import User
from rest_framework.fields import ReadOnlyField
from rest_framework.relations import PrimaryKeyRelatedField, HyperlinkedIdentityField
from rest_framework.serializers import HyperlinkedModelSerializer

from realworld.apps.quickstart.models import Snippet


class UserSerializer(HyperlinkedModelSerializer):
    snippets = PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

    class Meta:
        model = User
        fields = ['id', 'username', 'snippets']


class SnippetSerializer(HyperlinkedModelSerializer):
    owner = ReadOnlyField(source='owner.username')
    highlight = HyperlinkedIdentityField(view_name='snippet-highlight', format='html')

    class Meta:
        model = Snippet
        fields = ['url', 'id', 'highlight', 'owner',
                  'title', 'code', 'linenos', 'language', 'style']
