from django.urls import path

from realworld.apps.profiles.views import ProfileRetrieveAPIView, ProfileFollowAPIView

urlpatterns = [
    path(
        'profiles/<username>/',
        ProfileRetrieveAPIView
    ),
    path(
        'profiles/<username>/follow/',
        ProfileFollowAPIView.as_view()
    )
]
