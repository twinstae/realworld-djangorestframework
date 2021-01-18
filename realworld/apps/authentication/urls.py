from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

urlpatterns = [
    path('', RegistrationAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('<int:pk>/', UserRetrieveUpdateAPIView.as_view()),
]
