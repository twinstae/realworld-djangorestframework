from django.conf.urls import url
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from realworld.apps.articles.views import ArticleViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('', include(router.urls))
]
