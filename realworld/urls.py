from django.urls import path, include
from rest_framework.routers import DefaultRouter


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('api/', include(('realworld.apps.articles.urls', 'realworld.apps.articles')), name='articles'),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
