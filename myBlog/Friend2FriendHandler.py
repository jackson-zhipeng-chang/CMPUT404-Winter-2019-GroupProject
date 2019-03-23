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
from . import Helpers

class Friend2FriendHandler(APIView):
    def get(self, request, authorid1, service2, authorid2, format=None):
        author1_obj = Helpers.get_author_or_not_exits(authorid1)
        author2_obj = Helpers.get_author_or_not_exits(authorid2)
        if (author1_obj is not False) and (author2_obj is not False):
            isFriend = Helpers.check_two_users_friends(authorid1, authorid2)
            authors = []
            authors.append(author1_obj.host+"service/author/"+str(author1_obj.id))
            authors.append(author2_obj.host+"service/author/"+str(author2_obj.id))
            response_body = {
                "query":"friends",
                "authors": authors,
                "friends": isFriend
            }
            return Response(response_body, status=status.HTTP_200_OK)
        else:
            return Response("User not found", status=404)

