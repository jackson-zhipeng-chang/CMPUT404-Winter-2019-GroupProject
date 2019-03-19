from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
import urllib 

class Friend2FriendHandler(APIView):
    def get(self, request, authorid1, service2, authorid2, format=None):
        print(authorid1, service2, authorid2)
        return Response("Ok", status=status.HTTP_200_OK)

