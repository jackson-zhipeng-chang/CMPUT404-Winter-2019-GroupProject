import markdown
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework import status
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser
from . import Helpers

class NewPostHandler(APIView):
    def post(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        author = Helpers.get_author_or_not_exits(current_user_uuid)
        origin = Helpers.get_host_from_request(request)
        data = request.data
        if (data["contentType"] == "text/markdown"):
            data["content"] = markdown.markdown(data["content"])
        serializer = PostSerializer(data=data, context={'author': author,'origin': origin})
        if serializer.is_valid():
            serializer.save()
            responsBody={
                "query": "addPost",
                "success":True,
                "message":"Post Added"
                }
            return Response(responsBody, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
 

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
class PostHandler(APIView):
    def get(self, request,postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post couldn't find", status=404)
        else:
            post = Post.objects.get(pk=postid)
            serializer = PostSerializer(post)
            unlisted_post = post.unlisted

            if unlisted_post:
                return JsonResponse(serializer.data, status=200)

            else:
                user_verified = Helpers.verify_current_user_to_post(post, request)
                if user_verified:
                    return JsonResponse(serializer.data, status=200)
                else:
                    return HttpResponse("You don't have the access to the post",status=404)
    def put(self, request, postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post coudn't find", status=404)
        else:
            post = Post.objects.get(pk=postid)
            current_user_uuid = Helpers.get_current_user_uuid(request)

            if current_user_uuid==post.author_id:
                data = request.data
                serializer = PostSerializer(post, data=data)

                if serializer.is_valid():
                    serializer.save()
                    return JsonResponse(serializer.data)
                return JsonResponse("Data is not valid", serializer.errors, status=400)
            else:
                return HttpResponse("You don't have the access to the post",status=404)

    def delete(self, request, postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post coudn't find", status=404)
            
        else:
            post = Post.objects.get(pk=postid)
            current_user_uuid = Helpers.get_current_user_uuid(request)
            if current_user_uuid==post.author_id:
                post.delete()
                return HttpResponse("Success deleted",status=204)
            else:
                return HttpResponse("You don't have the access to the post",status=404)


# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset
# https://github.com/belatrix/BackendAllStars/blob/master/employees/views.py
# https://github.com/belatrix/BackendAllStars/blob/master/employees/serializers.py
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
# https://stackoverflow.com/questions/2658291/get-list-or-404-ordering-in-django
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=current_user_uuid) | Q(visibility='PUBLIC'))
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts_list, request)
        serializer=PostSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data) 


# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset
class PostToUserIDHandler(APIView):
    def get(self, request, user_id, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=user_id), Q(visibility='PUBLIC'))
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts_list, request)
        serializer=PostSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)  