from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from realworld.apps.articles.views import ArticleViewSet, ArticlesFeedAPIView, ArticlesFavoriteAPIView, \
    CommentsListCreateAPIView, CommentsDestroyAPIView, TagListAPIView

router = DefaultRouter(trailing_slash=False)
router.register('articles', ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    url(r'^articles/feed/?$',
        ArticlesFeedAPIView.as_view()),
    url(r'^articles/(?P<article_slug>[-\w]+)/favorite/?$',
        ArticlesFavoriteAPIView.as_view()),
    url(r'^articles/(?P<article_slug>[-\w]+)/comments/?$',
        CommentsListCreateAPIView.as_view()),
    url(r'^articles/(?P<article_slug>[-\w]+)/comments/(?P<comment_pk>[\d]+)/?$',
        CommentsDestroyAPIView.as_view()),
    url(r'^tags/?$',
        TagListAPIView.as_view()),
]
