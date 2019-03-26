from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend, Node, RemoteUser
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from urllib.parse import urlparse
from . import Helpers
from uuid import UUID
import datetime

class FriendRequestHandler(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if type(current_user_uuid) == UUID:
            author_object = Author.objects.get(id=current_user_uuid)
            friendrequests = Friend.objects.filter(friend=author_object, status='Pending')
            serializer = FriendSerializer(friendrequests, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return current_user_uuid

    def post(self, request, format=None):
        data = request.data
        if data['query'] == 'friendrequest':
            current_user_uuid = Helpers.get_current_user_uuid(request)
            author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
            sender_object = Author.objects.get(id=author_id)
            reciver_object = Author.objects.get(id=friend_id)
            friend_already = Helpers.check_two_users_friends(author_id,friend_id)
            if (not friend_already):
                if (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Decline").exists()):
                    friendrequest = Friend.objects.get(author=sender_object, friend=reciver_object)
                    friendrequest.status="Pending"
                    friendrequest.save()
                    return Response("Friend request sent", status=status.HTTP_200_OK) 
                elif (Friend.objects.filter(author=reciver_object, friend=sender_object, status="Decline").exists()):
                    friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                    friendrequest.status="Accept"
                    friendrequest.save()
                    return Response("You are now friend with %s"%author_id, status=status.HTTP_200_OK)

                elif Friend.objects.filter(author=reciver_object, friend=sender_object, status="Pending").exists():
                    # if the one who I want to follow has followed me
                    friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                    friendrequest.status = 'Accept'
                    friendrequest.save()
                    return Response("You are new friend with{}".format(reciver_object.displayName, status=status.HTTP_200_OK))

                elif (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Pending").exists()): 
                    return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)  
                else:
                    friendrequest = Friend.objects.create(author=sender_object, friend=reciver_object)
                    friendrequest.save()
                    return Response("Friend request sent", status=status.HTTP_200_OK)  
            else:
                return Response("You are already friends", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("You are not sending the friendrequest with the correct format. Missing 'query': 'friendrequest'",status=status.HTTP_400_BAD_REQUEST)  

    def put(self, request, format=None):
        data = request.data
        try:
            requestid = data['id']
        except:
            return Response('No request id', status=404)

        if (not Friend.objects.filter(id=requestid).exists()):
            responsBody={
                "query": "friendrequestRespons",
                "success":False,
                "message":"Request not found"
                }
            return Response(responsBody, status=404)
        else:
            data = request.data
            current_user_uuid = Helpers.get_current_user_uuid(request)
            friendrequests=Friend.objects.get(id=requestid)
            if (current_user_uuid == friendrequests.author.id) or (current_user_uuid == friendrequests.friend.id):
                newStatus = data['status']
                if newStatus in ['Accept', 'Decline']:
                    friendrequests.status=newStatus
                    friendrequests.last_modified_time = datetime.datetime.now()
                    friendrequests.save()
                    return Response("Success responded", status=status.HTTP_200_OK)
                else:
                    return Response("Status not valid", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Opreation not allowed.", status=status.HTTP_400_BAD_REQUEST)

class MyFriends(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        friends_list = Helpers.get_friends(current_user_uuid)
        serializer = AuthorSerializer(friends_list, many=True)
        return JsonResponse(serializer.data, safe=False)
            
class UnFriend(APIView):
    def delete(self, request, friendid, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if (Friend.objects.filter(Q(author=current_user_uuid), Q(status='Accept')).exists()):
            Friend.objects.filter(Q(author=current_user_uuid), Q(status='Accept')).delete()
            return Response("Deleted", status=200)

        if (Friend.objects.filter(Q(author=friendid), Q(status='Accept')).exists()):
            Friend.objects.filter(Q(author=friendid), Q(status='Accept')).delete()
            return Response("Deleted", status=200)

        # case that, A requests B, before B accepts/declines this request, A sends an unFriend request to B
        elif (Friend.objects.filter(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Pending')).exists()):
            Friend.objects.filter(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Pending')).delete()
            return Response("Cancel friend request",status=200)
        elif(Friend.objects.filter(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Decline')).exists()):
            Friend.objects.filter(Q(author=current_user_uuid), Q(friend=friendid), Q(status='Decline')).delete()
            return Response("Delete friend request",status=200)
        else:
            return Response("You are not friend yet", status=400)