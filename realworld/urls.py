from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Real World API by DRF",
      default_version='v1',
      description="Real World api spec 에 따라 제작한 Django Rest Framework 구현",
      contact=openapi.Contact(email="rabolution@gmail.com"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('realworld.apps.articles.urls'), name='articles'),
    path('api/users/', include('realworld.apps.authentication.urls'), name='authentication'),
    path('api/profiles/', include('realworld.apps.profiles.urls'), name='profiles'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
