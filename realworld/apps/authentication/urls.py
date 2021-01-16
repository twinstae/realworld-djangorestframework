from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

urlpatterns = [
    path('<int:pk>/', UserRetrieveUpdateAPIView.as_view()),
    path('', RegistrationAPIView.as_view()),
    path('login/<int:pk>/', LoginAPIView.as_view()),
]
