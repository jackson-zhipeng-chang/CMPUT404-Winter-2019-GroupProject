from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Author,Friend
from .serializers import FriendSerializer
from rest_framework import status
from django.http import JsonResponse
from .import Helpers
from django.db.models import Q

class FriendStatusQueryHandler(APIView):
    def get(self,request,author_id,format=None):
        # author_id means the id of the author i am currently looking for
        current_user_uuid = Helpers.get_current_user_uuid(request)
        current_user_object = Author.objects.get(id=current_user_uuid)
        friend_object = Author.objects.get(id=author_id)
        relation_author_to_friend = Friend.objects.filter(Q(author=current_user_object) & Q(friend=friend_object) & Q(status='Aceept'))
        relation_friend_to_author = Friend.objects.filter(Q(author=friend_object) & Q(friend=current_user_object) & Q(status='Aceept'))
        if relation_author_to_friend or relation_friend_to_author:
            responseBody = {
                "query":"friends",
                "friends":"true",
            }

            return Response(responseBody,status=status.HTTP_200_OK)

        else:
            responseBody = {
                "query":"friends",
                "friends":"false",
            }
            return Response(responseBody,status=status.HTTP_200_OK)