from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('realworld.apps.articles.urls'), name='articles'),
    path('api/', include('realworld.apps.authentication.urls'), name='authentication'),
    path('api/', include('realworld.apps.profiles.urls'), name='profiles'),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
