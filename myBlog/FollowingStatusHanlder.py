from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Author,Friend
from rest_framework import status
from .import Helpers

class FollowingStatusHanlder(APIView):
    def get(self,request,author_id,format=None):
        print('here')
        # author_id means the id of the author i am currently looking for
        current_user_uuid = Helpers.get_current_user_uuid(request)
        current_user_object = Author.objects.get(id=current_user_uuid)
        friend_object = Author.objects.get(id=author_id)

        try:
            relation_author_to_friend = Friend.objects.filter(author=current_user_object,friend=friend_object)[0]
            current_status = relation_author_to_friend.status

            responseBody = {
                "author":current_user_uuid,
                "friend":author_id,
                "status":current_status,
            }
            return Response(responseBody,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            responseBody = {
                "author": current_user_uuid,
                "friend": author_id,
                "status": "notFound",
            }
            return Response(responseBody,status=status.HTTP_200_OK)
