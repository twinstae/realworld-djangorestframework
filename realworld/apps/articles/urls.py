from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from realworld.apps.articles.views import ArticleViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
