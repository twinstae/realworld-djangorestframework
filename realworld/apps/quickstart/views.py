from django.contrib.auth.models import User
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse

from realworld.apps.quickstart.models import Snippet
from realworld.apps.quickstart.serializers import UserSerializer, SnippetSerializer


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'snippets': reverse('snippet-list', request=request, format=format)
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class SnippetViewSet(
    viewsets.ModelViewSet
):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
