from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend, Node, RemoteUser
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
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
                url = friend.friend.host+"service/author/"+str(friend.friend.id)
                if url not in friends_list:
                    friends_list.append(url)

            for friend in friendsIndirect:
                url = friend.author.host+"service/author/"+str(friend.author.id)
                if url not in friends_list:
                    friends_list.append(url)

            responsBody = { 
            "query":"friends",
            "authors":friends_list,
            }
            return Response(responsBody, status=status.HTTP_200_OK)

    def post(self, request, user_id, format=None):
        # try:
        author = Helpers.get_author_or_not_exits(user_id)
        data = request.data
        print("request data is {}: ".format(data))
        if data['query'] == 'friends':
            # friends_list = Helpers.get_friends(user_id)
            # get friendlist locally
            friend_list = Friend.objects.filter(Q(author=author)|Q(friend=author))
            print("local friendlist is {}:".format(friend_list))
            if type(data['authors'])!= list:
                query_list = []
                query_list.append(data['authors'])
            else:
                query_list = data['authors']
            print("query_list is {}:".format(query_list))
            respons_list = []
            for author_url in query_list:
                for friend_obj in friend_list:
                    # can be author or friend in a relationship
                    firend_uuid = str(friend_obj.friend.id)
                    author_uuid = str(friend_obj.author.id)
                    if firend_uuid in author_url or author_uuid in author_url:
                        respons_list.append(author_url)
            responsBody={
                "query": "friends",
                "author":author.host+"service/author/"+str(author.id),
                "authors":respons_list
            }
            return Response(responsBody, status=200)
        else:
            return Response("You are not sending the request with the correct format. Missing 'query': 'friends'",status=status.HTTP_400_BAD_REQUEST)
        # except:

            # return Response("Author couldn't find", status=404)