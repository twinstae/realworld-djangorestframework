from rest_framework import mixins, viewsets, status, generics
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from realworld.apps.articles.models import Article, Tag, Comment
from realworld.apps.articles.renderers import ArticleJSONRenderer, CommentJSONRenderer
from realworld.apps.articles.serializers import ArticleSerializer, TagSerializer, CommentSerializer
from realworld.strings import ARTICLE_DOES_NOT_EXIST


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
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        queryset = self.queryset
        author = self.request.query_params.get('author', None)
        if author is not None:
            queryset.filter(author__user__username=author)
        tag = self.request.query_params.get('tag', None)
        if tag is not None:
            queryset = queryset.filter(tags__tag=tag)

        favorited_by = self.request.query_params.get('favorited', None)
        if favorited_by is not None:
            queryset = queryset.filter(
                favorited_by__user__username=favorited_by
            )
        return queryset

    def create(self, request, *args, **kwargs):
        serializer_context = {
            'author': request.user.profile,
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


class CommentsListCreateAPIView(generics.ListCreateAPIView):
    lookup_field = 'article__slug'
    lookup_url_kwarg = 'article_slug'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.select_related(
        'article', 'article__author', 'article__author__user',
        'author', 'author__user'
    )
    renderer_classes = (CommentJSONRenderer,)
    serializer_class = CommentSerializer

    def filter_queryset(self, queryset):
        # The built-in list function calls `filter_queryset`. Since we only
        # want comments for a specific article, this is a good place to do
        # that filtering.
        filters = {self.lookup_field: self.kwargs[self.lookup_url_kwarg]}
        return queryset.filter(**filters)

    def create(self, request, article_slug=None):
        data = request.data.get('comment', {})
        context = {'author': request.user.profile}

        try:
            context['article'] = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentsDestroyAPIView(generics.DestroyAPIView):
    lookup_url_kwarg = 'comment_pk'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()

    def destroy(self, request, article_slug=None, comment_pk=None):
        comment = self.get_comment_or_404(comment_pk)
        comment.delete()

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def get_comment_or_404(comment_pk):
        try:
            comment = Comment.objects.get(pk=comment_pk)
        except Comment.DoesNotExist:
            raise NotFound('A comment with this ID does not exist.')
        return comment


class ArticlesFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def delete(self, request, article_slug=None):
        return self.context(
            request, article_slug,
            strategy=lambda profile, article: profile.unfavorite(article),
            status_code=status.HTTP_200_OK
        )

    def post(self, request, article_slug=None):
        return self.context(
            request, article_slug,
            strategy=lambda profile, article: profile.favorite(article),
            status_code=status.HTTP_201_CREATED
        )

    def context(self, request, article_slug, strategy, status_code):
        profile = self.request.user.profile
        serializer_context = {'request': request}

        try:
            article = Article.objects.get(slug=article_slug)
        except Article.DoesNotExist:
            raise NotFound(ARTICLE_DOES_NOT_EXIST)

        strategy(profile, article)

        serializer = self.serializer_class(article, context=serializer_context)

        return Response(serializer.data, status=status_code)


class TagListAPIView(generics.ListAPIView):
    queryset = Tag.objects.all()
    pagination_class = None
    permission_classes = (AllowAny,)
    serializer_class = TagSerializer

    def list(self, request):
        serializer_data = self.get_queryset()
        serializer = self.serializer_class(serializer_data, many=True)

        return Response({
            'tags': serializer.data
        }, status=status.HTTP_200_OK)


class ArticlesFeedAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Article.objects.all()
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            author__in=self.request.user.profile.follows.all()
        )

    def list(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        serializer_context = {'request': request}
        serializer = self.serializer_class(
            page, context=serializer_context, many=True
        )

        return self.get_paginated_response(serializer.data)
