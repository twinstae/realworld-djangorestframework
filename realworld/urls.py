from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from realworld.apps.quickstart import views

router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet)
router.register(r'users', views.UserViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
    path('api/', include(('realworld.apps.articles.urls', 'realworld.apps.articles')), name='articles'),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
