from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Author, Comment, Friend
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views import generic
from django.db.models import Q
from django.shortcuts import render

def get_author_or_not_exits(current_user_uuid):
    if (not Author.objects.filter(id=current_user_uuid).exists()):
        return Response("Author coudn't find", status=404)
    else:
        return Author.objects.get(id=current_user_uuid)

def get_host_from_request(request):
# https://docs.djangoproject.com/en/2.1/ref/request-response/
    host = request.scheme+"://"+request.get_host()
    return host
    
def get_current_user_uuid(request):
    if (not User.objects.filter(pk=request.user.id).exists()):
        print(request.user.id)
        print("User coudn't find")
        return Response("User coudn't find", status=404)
    else:
        current_user = User.objects.get(pk=request.user.id)
        author = get_object_or_404(Author, user=current_user)
        return author.id

def verify_current_user_to_post(post, request):
    post_visibility = post.visibility
    post_author = post.author_id
    unlisted_post = post.unlisted
    if unlisted_post:
        return True
    else:
        if User.objects.filter(pk=request.user.id).exists():
            current_user_uuid = get_current_user_uuid(request)
            if current_user_uuid == post_author: 
                return True
            else:
                if post_visibility == 'PUBLIC':
                    return True
                elif post_visibility == 'FOAF':
                    return True
                elif post_visibility == 'FRIENDS':
                    friend = check_two_users_friends(post_author,current_user_uuid)
                    if friend:
                        return True
                    else:
                        return False
                elif (post_visibility == 'PRIVATE') and (current_user_uuid != post_author):
                    return False
                elif post_visibility == 'SERVERONLY':
                    current_server = get_host_from_request(request)
                    user_server = Author.objects.get(id=current_user_uuid).host
                    if current_server == user_server:
                        return True
                    else:
                        return False
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

def posts_list(request):
    url = "/myBlog/author/posts/?size=10"
    return render(request, 'posts.html', {"url":url, "trashable":"false"})

def new_post(request):
    return render(request, 'newpost.html')

def my_posts(request):
    my_uuid = get_current_user_uuid(request)
    url = "/myBlog/author/%s/posts/?size=10"%my_uuid
    return render(request, 'posts.html', {"url":url, "trashable":"true"})