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

def logout_user(request):
    logout(request)
    return redirect("home")
    
# ---------------------------------------------------------------------End of helper functions---------------------------------------------------------------------  
 