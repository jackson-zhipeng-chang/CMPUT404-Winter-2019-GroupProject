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

class FriendRequestHandler(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        author_object = Author.objects.get(id=current_user_uuid)
        friendrequests = Friend.objects.filter(friend=author_object, status='Pending')
        serializer = FriendSerializer(friendrequests, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, format=None):
        data = request.data
        if data['query'] == 'friendrequest':
            current_user_uuid = Helpers.get_current_user_uuid(request)
            author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
            sender_object = Author.objects.get(id=author_id)
            reciver_object = Author.objects.get(id=friend_id)
            friend_already = Helpers.check_two_users_friends(author_id,friend_id)
            if (str(current_user_uuid) == author_id):
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

                    elif (Friend.objects.filter(author=sender_object, friend=reciver_object, status="Pending").exists()): 
                        return Response("Friend request already sent", status=status.HTTP_400_BAD_REQUEST)  

                    else:
                        friendrequest = Friend.objects.create(author=sender_object, friend=reciver_object)
                        friendrequest.save()
                        return Response("Friend request sent", status=status.HTTP_200_OK)  
                else:
                    return Response("You are already friends", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Please login to correct account", status=status.HTTP_400_BAD_REQUEST)
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
                    friendrequests.save()
                    return Response("Success responded", status=status.HTTP_200_OK)
                else:
                    return Response("Status not valid", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Opreation not allowed.", status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, format=None): #TODO: We actually don't need this function
        data = request.data
        if data['query'] == 'unfriend':
            current_user_uuid = Helpers.get_current_user_uuid(request)
            author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
            sender_object = Author.objects.get(id=author_id)
            reciver_object = Author.objects.get(id=friend_id)
            friendship = Friend.objects.get_object_or_404(author=sender_object, friend=reciver_object)
            current_status = friendship.status

            if (current_user_uuid == friendrequests.author.id and (current_status == 'Pending' or current_status == 'Decline')):
                friendrequests.delete()
                return Response("Success unfriend, you have stopped following your friend", status=status.HTTP_200_OK)

            elif (current_user_uuid == friendrequests.friend.id and current_status == 'Accept'):
                friendrequests.status='Decline'
                friendrequests.save()
                return Response("Success unfriend, your friend is still following you", status=status.HTTP_200_OK)
                
            else:
                return Response("Opreation not allowed.", status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("You are not sending the friendrequest with the correct format. Missing 'query': 'unfriend'",status=status.HTTP_400_BAD_REQUEST)    
 
