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

def get_friends():
    return True
          
def get_followings():
    return True

def check_two_users_friends(author1_id,author2_id):
    author1_object = Author.objects.get(id=author1_id)
    author2_object = Author.objects.get(id=author2_id)
    friend1To2 = Friend.objects.filter(author=author1_object, friend=author2_object, status="Accept").exists()
    friend2To1 = Friend.objects.filter(author=author2_object, friend=author1_object, status="Accept").exists()
    if friend1To2 or friend2To1:
        return True
    else:
        return False

def check_author1_follow_author2(author1_id,author2_id):
    author1_object = Author.objects.get(id=author1_id)
    author2_object = Author.objects.get(id=author2_id)
    declined = Friend.objects.filter(author=author1_object, friend=author2_object, status="Decline").exists()
    pending = Friend.objects.filter(author=author1_object, friend=author2_object, status="Pending").exists()

    if declined or pending:
        return True
    else:
        return False

# ---------------------------------------------------------------------End of helper functions---------------------------------------------------------------------
# https://stackoverflow.com/questions/37752440/relative-redirect-using-meta-http-equiv-refresh-with-gh-pages
# https://www.tutorialspoint.com/How-to-automatically-redirect-a-Web-Page-to-another-URL for redirecting
# Code from: Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/2.1/topics/auth/default/

class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm  # The Form class the FormView should use
    success_url = '/myBlog/author/posts/'  # Go here after successful POST

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = User.objects.create_user(username=username, password=password, is_active=False)
        try:
            host = get_host_from_request(self.request)
            author = Author.objects.create(displayName=username,user=user, host=host)
            author.save()
        except:
            user.delete()
            return Response("User coudn't create", status=400)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm # The Form class the FormView should use
    success_url = '/myBlog/author/posts/'  # Go here after successful POST

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        else:
            return Response("User coudn't find", status=404)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def logout_user(request):
    logout(request)
    return redirect("home")

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

            return Response("Post couldn't find", status=404)

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
        data = request.data
        if data['query'] == 'addComment':
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

        else:
            return Response("You are not sending the friendrequest with the correct format. Missing 'query': 'addComment'",status=status.HTTP_400_BAD_REQUEST)



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
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=user_id), Q(visibility='PUBLIC'))
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
            current_user_uuid = get_current_user_uuid(request)
            author_id = data['author']['id'].replace(data['author']['host']+'author/', "")
            friend_id = data['friend']['id'].replace(data['friend']['host']+'author/', "")
            sender_object = Author.objects.get(id=author_id)
            reciver_object = Author.objects.get(id=friend_id)
            friend_already = check_two_users_friends(author_id,friend_id)

            if (current_user_uuid == author_id):
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
            current_user_uuid = get_current_user_uuid(request)
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
            current_user_uuid = get_current_user_uuid(request)
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
                url = friend.friend.host+"/myBlog/author/"+str(friend.friend.id)
                if url not in friends_list:
                    friends_list.append(url)

            for friend in friendsIndirect:
                url = friend.author.host+"/myBlog/author/"+str(friend.author.id)
                if url not in friends_list:
                    friends_list.append(url)

            responsBody = { 
            "query":"friends",
            "authors":friends_list,
            "friends": True
            }
            return Response(responsBody, status=status.HTTP_200_OK)

@login_required(login_url="home")
@api_view(['GET'])
def Friend2FriendHandler(request, user_id1, user_id2):
    if request.method == 'GET':
    	return Response({"message": "GET method", "data": post})    
 