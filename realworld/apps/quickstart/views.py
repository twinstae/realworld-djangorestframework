from django.contrib.auth.models import User, Group
from django.http import HttpResponse, Http404
from rest_framework import mixins, generics
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from realworld.apps.quickstart.models import Snippet
from realworld.apps.quickstart.serializers import UserSerializer, GroupSerializer, SnippetSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class SnippetList(
    generics.ListCreateAPIView
):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer


class SnippetDetail(
    generics.RetrieveUpdateDestroyAPIView
):
    """
    Retrieve, update or delete a code snippet.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
