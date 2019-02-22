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
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from urllib.parse import urlparse

# https://stackoverflow.com/questions/37752440/relative-redirect-using-meta-http-equiv-refresh-with-gh-pages
# https://www.tutorialspoint.com/How-to-automatically-redirect-a-Web-Page-to-another-URL for redirecting

# Code from: Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/2.1/topics/auth/default/





# ---------------------------------------------------------------------Helper functions---------------------------------------------------------------------
def get_author_or_not_exits(current_user_uuid):
    if (not Author.objects.filter(id=current_user_uuid).exists()):
        return Response("Author coudn't find", status=404)
    else:
        return Author.objects.get(id=current_user_uuid)

def get_host_from_request(request):
# https://docs.djangoproject.com/en/2.1/ref/request-response/
    host = request.scheme+"://"+request.get_host()
    return host

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username=username,password=password, is_active=False)
            userObj = get_object_or_404(User, username=username)
# https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
            host = get_host_from_request(request)
            author = Author.objects.create(displayName=username,user=userObj, host=host)
            author.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def get_current_user_uuid(request):
    if (not User.objects.filter(pk=request.user.id).exists()):
        return Response("User coudn't find", status=404)
    else:
        current_user = User.objects.get(pk=request.user.id)
        author = get_object_or_404(Author, user=current_user)
        return author.id

def verify_current_user_to_post(post, request):
    current_user_uuid = get_current_user_uuid(request)
    post_visibility = post.visibility
    post_author = post.author_id
    unlisted_post = post.unlisted


    if User.objects.filter(pk=request.user.id).exists():
        if unlisted_post:
            return True

        elif (post_visibility == 'PUBLIC') or (post_visibility == 'PRIVATE' and current_user_uuid == post_author):
            return True

        else:
            return False

    elif (not User.objects.filter(pk=request.user.id).exists()):
        if unlisted_post:
            return True

        else:
            return False

def get_friends(self):
    connections = Friend.objects.filter(user=self.user)
    return connections
          
def get_followings(self):
    followings = Friend.objects.filter(friend=self.user)
    return followings
# ---------------------------------------------------------------------End of helper functions---------------------------------------------------------------------

# https://www.django-rest-framework.org/api-guide/views/
# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
# https://www.geeksforgeeks.org/python-uploading-images-in-django/
# https://stackoverflow.com/questions/4093999/how-to-use-django-to-get-the-name-for-the-host-server
class NewPostHandler(APIView):
    def post(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
        author = get_author_or_not_exits(current_user_uuid)
        data = request.data
        origin=get_host_from_request(request)
        serializer = PostSerializer(data=data, context={'author': author, 'origin': origin})
        if serializer.is_valid():
            serializer.save()
            responsBody={
                "query": "addPost",
                "success":True,
                "message":"Post Added"
                }
            return Response(responsBody, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
class PostHandler(APIView):
    def get(self, request,postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post coudn't find", status=404)

        else:
            post = Post.objects.get(pk=postid)
            serializer = PostSerializer(post)
            unlisted_post = post.unlisted

            if unlisted_post:
                return JsonResponse(serializer.data, status=200)

            else:
                user_verified = verify_current_user_to_post(post, request)
                if user_verified:
                    return JsonResponse(serializer.data, status=200)
                else:
                    return HttpResponse("You don't have the access to the post",status=404)
  
    def put(self, request, postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post coudn't find", status=404)
            
        else:
            post = Post.objects.get(pk=postid)
            current_user_uuid = get_current_user_uuid(request)

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
            current_user_uuid = get_current_user_uuid(request)
            if current_user_uuid==post.author_id:
                post.delete()
                return HttpResponse("Success deleted",status=204)
            else:
                return HttpResponse("You don't have the access to the post",status=404)


class CommentHandler(APIView):
    def get(self, request, postid, format=None):
        post = Post.objects.get(pk=postid)
        if (not verify_current_user_to_post(post, request)):
            responsBody={
                "query": "addComment",
                "success":False,
                "message":"Comment not allowed"
                }
            return Response(responsBody, status=403)
        else:
            current_user_uuid = get_current_user_uuid(request)
            comments_list = get_list_or_404(Comment,postid=postid)
            paginator = CustomPagination()
            results = paginator.paginate_queryset(comments_list, request)
            serializer=CommentSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)

    def post(self, request, postid, format=None):
        post = Post.objects.get(pk=postid)
        if (not verify_current_user_to_post(post, request)):
            responsBody={
                "query": "addComment",
                "success":False,
                "message":"Comment not allowed"
                }
            return Response(responsBody, status=404)
        else:
            current_user_uuid = get_current_user_uuid(request)
            author = get_author_or_not_exits(current_user_uuid)
            data = request.data
            serializer = CommentSerializer(data=data, context={'author': author, 'postid':postid})
            if serializer.is_valid():
                serializer.save()
                responsBody={
                "query": "addComment",
                "success":True,
                "message":"Comment Added"
                }
                return Response(responsBody, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset
# https://github.com/belatrix/BackendAllStars/blob/master/employees/views.py
# https://github.com/belatrix/BackendAllStars/blob/master/employees/serializers.py
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
# https://stackoverflow.com/questions/2658291/get-list-or-404-ordering-in-django
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=current_user_uuid) | Q(visibility='PUBLIC'))
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts_list, request)
        serializer=PostSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)

# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset
class PostToUserIDHandler(APIView):
    def get(self, request, user_id, format=None):
        current_user_uuid = get_current_user_uuid(request)
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=user_id) | Q(visibility='PUBLIC'))
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts_list, request)
        serializer=PostSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)


class AuthorProfileHandler(APIView):
    def get(self, request, user_id, format=None):
        author = get_author_or_not_exits(user_id)
        serializer = AuthorSerializer(author)
        return JsonResponse(serializer.data)

    def put(self, request, user_id, format=None):
        data = request.data
        author = get_author_or_not_exits(user_id)
        current_user_uuid = get_current_user_uuid(request)
        if current_user_uuid == author.id:
            serializer = AuthorSerializer(author, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        else:
            return HttpResponse(status=404)
  
    def delete(self, request, user_id, format=None):
        author = get_author_or_not_exits(user_id)
        user = get_object_or_404(User, pk=author.user.id)
        current_user_uuid = get_current_user_uuid(request)
        if current_user_uuid == author.id:
            author.delete()
            user.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


class FriendRequestHandler(APIView):

    def get(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
        author_object = Author.objects.get(id=current_user_uuid)
        friendrequests = Friend.objects.filter(friend=author_object, status='Pending')
        serializer = FriendSerializer(friendrequests, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, format=None):
        data = request.data
        if data['query'] == 'friendrequest':
            try:
                author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
                friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
                author_object = Author.objects.get(id=author_id)
                friend_object = Author.objects.get(id=friend_id)
                friend = Friend.objects.create(author=author_object, friend=friend_object)
                friend.save()
                return Response(status=status.HTTP_200_OK)  
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)  
        else:
            return Response("You are not sending the friendrequest with the correct format.",status=status.HTTP_400_BAD_REQUEST)  


    def put(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
        author_object = Author.objects.get(id=current_user_uuid)
        friendrequests = Friend.objects.filter(friend=author_object, status='Pending')
        serializer = FriendSerializer(friendrequests, many=True)
        return JsonResponse(serializer.data, safe=False)




@login_required(login_url="home")
@api_view(['POST'])
def FriendQueryHandler(request, user_id):
    if request.method == 'POST':
    	return Response({"message": "POST method", "data": post})    

@login_required(login_url="home")
@api_view(['GET'])
def Friend2FriendHandler(request, user_id1, user_id2):
    if request.method == 'GET':
    	return Response({"message": "GET method", "data": post})    
 
