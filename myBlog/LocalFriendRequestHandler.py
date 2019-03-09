from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Author,Friend
from .serializers import FriendSerializer
from rest_framework import status
from django.http import JsonResponse
from . import Helpers

class LocalFriendRequestHandler(APIView):
    def post(self,request,format=None):
        data = request.data
        if data['query'] == 'friendrequest':
            current_user_uuid = Helpers.get_current_user_uuid(request)
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/',"")
            sender_obj = Author.objects.get(id=current_user_uuid)
            reciver_obj = Author.objects.get(id=friend_id)
            friend_already = Helpers.check_two_users_friends(current_user_uuid,friend_id)
            if not friend_already:
                if Friend.objects.filter(author=sender_obj,friend=reciver_obj,status='Pending').exists():
                    return Response("Friend request already sent",status=status.HTTP_400_BAD_REQUEST)
                elif Friend.objects.filter(author=reciver_obj,friend=sender_obj,status='Pending').exists():
                    friendrequest = Friend.objects.get(author=reciver_obj,friend=sender_obj)
                    friendrequest.status="Accept"
                    friendrequest.save()
                    return Response("You are now friend with %s" %current_user_uuid,status=status.HTTP_200_OK)
                else:
                    friendrequest = Friend.objects.create(author=sender_obj,friend=reciver_obj)
                    friendrequest.save()
                    return Response("Friend request sent", status=status.HTTP_200_OK)
            else:
                return Response("You are already friends",status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("You are not sending the friendrequest with the correct format. Missing 'query':'friendrequest'",
                            status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,format=None):
        data = request.data
        try:
            requestid = data['id']
        except:
            return Response('No request id',status=404)

        if not Friend.objects.filter(id=requestid).exists():
            responsBody={
                "query": "friendrequestRespons",
                "success": False,
                "message": "Request not found"
            }
            return Response(responsBody,status=404)
        else:
            data = request.data
            current_user_uuid = Helpers.get_current_user_uuid(request)
            friendrequests=Friend.objects.get(id=requestid)
            if current_user_uuid==friendrequests.friend.id or current_user_uuid == friendrequests.author.id:
                newStatus = data['status']
                if newStatus == 'Accept':
                    friendrequests.status=newStatus
                    friendrequests.save()
                    return Response("Success responded",status=status.HTTP_200_OK)
                elif newStatus == 'Decline':
                    print('decline')
                    friendrequests.delete()
                    return Response("Success decline",status=status.HTTP_200_OK)
                elif newStatus == 'Pending':
                    friendrequests.status = newStatus
                    friendrequests.save()
                    return Response("Success Unfollowed ", status=status.HTTP_200_OK)

                else:
                    return Response('Status not valid',status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Opreation not allowed.",status=status.HTTP_400_BAD_REQUEST)


