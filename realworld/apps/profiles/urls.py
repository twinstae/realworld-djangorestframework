from django.conf.urls import url

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView

urlpatterns = [
    url(r'^(?P<username>\w+)/?$',
        ProfileRetrieveAPIView.as_view()),
    url(r'^(?P<username>\w+)/follow/?$',
        ProfileFollowAPIView.as_view()),
]
