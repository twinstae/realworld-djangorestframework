from django.conf.urls import url

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView

urlpatterns = [
    url(r'^profiles/(?P<username>\w+)/?$',
        ProfileRetrieveAPIView.as_view()),
    url(r'^profiles/(?P<username>\w+)/follow/?$',
        ProfileFollowAPIView.as_view()),
]
