from django.urls import path

urlpatterns = [
    path(
        'profiles/<username>/',
        ProfileRetrieveAPIView.as_View()
    ),
    path(
        'profiles/<username>/follow/',
        ProfileFollowAPIView.as_view()
    )
]