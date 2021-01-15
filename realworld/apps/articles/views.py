from rest_framework import mixins, viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from realworld.apps.articles.models import Article
from realworld.apps.articles.serializers import ArticleSerializer


class ArticleJSONRenderer(object):
    pass


class ArticleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    queryset = Article.objects.select_related('author', 'author__user')
    permission_classes = IsAuthenticatedOrReadOnly
    renderer_classes = (ArticleJSONRenderer, )
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset.filter(author__user__username=author)
        return queryset

    def create(self, request,  *args, **kwargs):
        serializer_context = {
            'author': request.user.profile,
            'request': request
        }

        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            data=serializer_data, context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
