from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import FormView
from django.db.models import Q
from urllib.parse import urlparse
from . import Helpers

class AuthorProfileHandler(APIView):
    def get(self, request, user_id, format=None):
        author = Helpers.get_author_or_not_exits(user_id)
        serializer = AuthorSerializer(author)
        return JsonResponse(serializer.data)

    def put(self, request, user_id, format=None):
        data = request.data
        author = Helpers.get_author_or_not_exits(user_id)
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if current_user_uuid == author.id:
            serializer = AuthorSerializer(author, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        else:
            return HttpResponse(status=404)
  
    def delete(self, request, user_id, format=None):
        author = Helpers.get_author_or_not_exits(user_id)
        user = get_object_or_404(User, pk=author.user.id)
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if current_user_uuid == author.id:
            author.delete()
            user.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)   


class MyProfileHandler(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        author = Helpers.get_author_or_not_exits(current_user_uuid)
        serializer = AuthorSerializer(author)
        return JsonResponse(serializer.data)