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

class FriendQueryHandler(APIView):
    def get(self, request, user_id, format=None):
        if (not Author.objects.filter(id=user_id).exists()):
            return Response("Author coudn't find", status=404)

        else:
            author_object = Author.objects.get(id=user_id)
            friendsDirect = Friend.objects.filter(Q(author=author_object), Q(status='Accept'))
            friendsIndirect = Friend.objects.filter(Q(friend=author_object), Q(status='Accept'))
            friends_list = []

            for friend in friendsDirect:
                url = friend.friend.host+"/myBlog/author/"+str(friend.friend.id)
                if url not in friends_list:
                    friends_list.append(url)

            for friend in friendsIndirect:
                url = friend.author.host+"/myBlog/author/"+str(friend.author.id)
                if url not in friends_list:
                    friends_list.append(url)

            responsBody = { 
            "query":"friends",
            "authors":friends_list,
            "friends": True
            }
            return Response(responsBody, status=status.HTTP_200_OK)