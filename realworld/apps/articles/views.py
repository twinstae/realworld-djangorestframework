from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from realworld.apps.articles.models import Article
from realworld.apps.articles.renderers import ArticleJSONRenderer
from realworld.apps.articles.serializers import ArticleSerializer
from realworld.apps.profiles.models import Profile
from realworld.strings import ARTICLE_DOES_NOT_EXIST, NO_SLUG_IN_QUERY


class ArticleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet
):
    lookup_field = 'slug'
    queryset = Article.objects.select_related('author', 'author__user')
    permission_classes = [IsAuthenticatedOrReadOnly]
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
            'author': Profile.objects.all()[0],
            'request': request
        }

        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            data=serializer_data,
            context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())

        serializer = self.serializer_class(
            data=page,
            context=serializer_context,
            many=True
        )
        serializer.is_valid()

        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, slug):
        context, instance = self.get_context_instance_from_slug(request, slug)
        serializer = self.serializer_class(
            instance,
            context=context
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        context, instance = self.get_context_instance_from_slug(request, slug)
        data = request.data.get('article', {})

        serializer = self.serializer_class(
            instance,
            context=context,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_context_instance_from_slug(self, request, slug):
        serializer_context = {'request': request}
        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound(ARTICLE_DOES_NOT_EXIST)
        return serializer_context, serializer_instance
