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
import json
import requests
from requests.auth import HTTPBasicAuth

class FriendRequestHandler(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            current_user_uuid = Helpers.get_current_user_uuid(request)
            if type(current_user_uuid) == UUID:
                author_object = Author.objects.get(id=current_user_uuid)
                friendrequests = Friend.objects.filter(friend=author_object, status='Pending')
                serializer = FriendSerializer(friendrequests, many=True)
                return JsonResponse(serializer.data, safe=False)

            else:
                return Response("No friend request found", status=404)
        else:
            return Response("Unauthorized", status=401)

    def post(self, request, format=None):
        if request.user.is_authenticated:
            is_to_remote = False
            self.node = None
            self.data = None
            data = request.data
            if data['query'] == 'friendrequest':
                request_url = data['friend']['host']
                for node in Node.objects.all():
                    if str(node.host) in str(request_url):
                        is_to_remote = True
                        self.node = node
                        self.data = data
                current_user_uuid = Helpers.get_current_user_uuid(request)
                if 'author/' in data['author']['id'] and 'author/' in data['friend']['id']:
                    author_id = data['author']['id'].split('author/')[1]
                    friend_id = data['friend']['id'].split('author/')[1]
                    try:
                        author_id = UUID(author_id)
                        friend_id = UUID(friend_id)
                    except:
                        return Response("Author/Friend id in bad format", status=400) 
                else:
                    try:
                        author_id = UUID(data['author']['id'])
                        friend_id = UUID(data['friend']['id'])
                    except:
                        return Response("Author/Friend id in bad format", status=400) 

                if is_to_remote:
                    sender_verified = Helpers.verify_remote_author(data['author'])
                    reciver_verified = Helpers.verify_remote_author(data['friend'])
                    if sender_verified and reciver_verified:
                        sender_object = Helpers.get_or_create_author_if_not_exist(data['author'])
                        reciver_object = Helpers.get_or_create_author_if_not_exist(data['friend'])
                    else:
                        return Response("Author not found", status=404) 
                else:
                    sender_object = Author.objects.get(pk=author_id)
                    reciver_object = Author.objects.get(pk=friend_id)
                friend_already = Helpers.check_two_users_friends(author_id,friend_id)
                if (not friend_already):
                    if (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Decline").exists()):
                        if is_to_remote:
                            remote_status = Helpers.send_FR_to_remote(self.node,self.data)
                        if (is_to_remote and remote_status==200) or not is_to_remote:
                            friendrequest = Friend.objects.get(author=sender_object, friend=reciver_object)
                            friendrequest.status="Pending"
                            friendrequest.save()
                        else:
                            return Response("Something wrong with sending FRequest", status=status.HTTP_400_BAD_REQUEST)

                        return Response("Friend request sent", status=status.HTTP_200_OK) 

                    elif (Friend.objects.filter(author=reciver_object, friend=sender_object, status="Decline").exists()):
                        friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                        friendrequest.status="Accept"
                        friendrequest.save()
                        if is_to_remote:
                            Helpers.send_FR_to_remote(self.node,self.data)
                        return Response("You are now friend with %s"%author_id, status=status.HTTP_200_OK)

                    elif Friend.objects.filter(author=reciver_object, friend=sender_object, status="Pending").exists():
                        # if the one who I want to follow has followed me
                        friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                        friendrequest.status = 'Accept'
                        friendrequest.save()
                        if is_to_remote:
                            Helpers.send_FR_to_remote(self.node,self.data)
                        return Response("You are new friend with{}".format(reciver_object.displayName, status=status.HTTP_200_OK))

                    elif (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Pending").exists()): 
                        return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)  
                    else:
                        friendrequest = Friend.objects.create(author=sender_object, friend=reciver_object)
                        friendrequest.save()
                        if is_to_remote:
                            Helpers.send_FR_to_remote(self.node,self.data)
                        return Response("Friend request sent", status=status.HTTP_200_OK)  
                else:
                    return Response("You are already friends", status=status.HTTP_400_BAD_REQUEST)


            else:
                return Response("You are not sending the friendrequest with the correct format. Missing 'query': 'friendrequest'",status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response("Unauthorized", status=401)

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
        if (Friend.objects.filter(Q(author=current_user_uuid), Q(friend=friendid), Q(status='Accept')).exists()):
            FriendshipOgj = Friend.objects.get(Q(author=current_user_uuid), Q(friend=friendid), Q(status='Accept'))
            FriendshipOgj.delete()
            return Response("Deleted", status=200)

        if (Friend.objects.filter(Q(author=friendid), Q(friend=current_user_uuid), Q(status='Accept')).exists()):
            FriendshipOgj = Friend.objects.get(Q(author=friendid),Q(friend=current_user_uuid), Q(status='Accept'))
            FriendshipOgj.delete()
            return Response("Deleted", status=200)

        # case that, A requests B, before B accepts/declines this request, A sends an unFriend request to B
        elif (Friend.objects.filter(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Pending')).exists()):
            FriendshipOgj = Friend.objects.get(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Pending'))
            FriendshipOgj.delete()
            return Response("Cancel friend request",status=200)

        elif(Friend.objects.filter(Q(author=current_user_uuid),Q(friend=friendid),Q(status='Decline')).exists()):
            FriendshipOgj = Friend.objects.get(Q(author=current_user_uuid), Q(friend=friendid), Q(status='Decline'))
            FriendshipOgj.delete()
            return Response("Delete friend request",status=200)
        else:
            return Response("You are not friend yet", status=400)

class AcceptFR(APIView):
    def post(self,request,format=None):
        is_to_remote = False
        self.remote_node = None
        self.request_data = None
        data = request.data
        if data['query'] == 'friendrequest':
            request_url = data['friend']['host']
            print("data is: %s"%str(data))
            for node in Node.objects.all():
                if str(node.host) in str(request_url):
                    is_to_remote = True
                    self.remote_node = node
                    self.request_data = data

            current_user_uuid = Helpers.get_current_user_uuid(request)
            # author_id = data['author']['id'].split('author/')[1]
            # friend_id = data['friend']['id'].split('author/')[1]
            author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
            data['author']['id'] = author_id
            data['friend']['id'] = friend_id
            sender_verified = Helpers.verify_remote_author(data['author'])
            reciver_verified = Helpers.verify_remote_author(data['friend'])
            if sender_verified and reciver_verified:
                sender_object = Helpers.get_or_create_author_if_not_exist(data['author'])
                reciver_object = Helpers.get_or_create_author_if_not_exist(data['friend'])
            else:
                return Response("Author not found", status=404) 

            friend_already = Helpers.check_two_users_friends(author_id,friend_id)
            if (not friend_already):
                if (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Decline").exists()):
                    if is_to_remote:
                        remote_status = Helpers.send_FR_to_remote(self.remote_node,self.request_data)
                    if (is_to_remote and remote_status==200) or not is_to_remote:
                        friendrequest = Friend.objects.get(author=sender_object, friend=reciver_object)
                        friendrequest.status="Accept"
                        friendrequest.save()
                    else:
                        return Response("Something wrong with sending FRequest", status=status.HTTP_400_BAD_REQUEST)

                    return Response("Friend request sent", status=status.HTTP_200_OK) 

                elif (Friend.objects.filter(author=reciver_object, friend=sender_object, status="Decline").exists()):
                    if is_to_remote:
                        remote_status = Helpers.send_FR_to_remote(self.remote_node,self.request_data)
                    if (is_to_remote and remote_status==200) or not is_to_remote:
                        friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                        friendrequest.status="Accept"
                        friendrequest.save()
                    else:
                        return Response("Something wrong with sending FRequest", status=status.HTTP_400_BAD_REQUEST)
                    
                    return Response("You are now friend with %s"%author_id, status=status.HTTP_200_OK)

                elif Friend.objects.filter(author=reciver_object, friend=sender_object, status="Pending").exists():
                    # if the one who I want to follow has followed me
                    if is_to_remote:
                        remote_status = Helpers.send_FR_to_remote(self.remote_node,self.request_data)
                    if (is_to_remote and remote_status==200) or not is_to_remote:
                        friendrequest = Friend.objects.get(author=reciver_object, friend=sender_object)
                        friendrequest.status = 'Accept'
                        friendrequest.save()
                    else:
                        return Response("Something wrong with sending FRequest", status=status.HTTP_400_BAD_REQUEST)
                        
                    return Response("You are new friend with{}".format(reciver_object.displayName, status=status.HTTP_200_OK))

                # elif (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Pending").exists()): 
                #     return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)  
                else:
                    if is_to_remote:
                        remote_status = Helpers.send_FR_to_remote(self.remote_node,self.request_data)
                    if (is_to_remote and remote_status==200) or not is_to_remote:
                        
                        friendrequest = Friend.objects.create(author=sender_object, friend=reciver_object)
                        friendrequest.save()
                    else:
                        return Response("Something wrong with sending FRequest", status=status.HTTP_400_BAD_REQUEST)
                        
                    return Response("Friend request sent", status=status.HTTP_200_OK)  
            else:
                return Response("You are already friends", status=status.HTTP_400_BAD_REQUEST)


        else:
            return Response("You are not sending the friendrequest with the correct format. Missing 'query': 'friendrequest'",status=status.HTTP_400_BAD_REQUEST)  

        return