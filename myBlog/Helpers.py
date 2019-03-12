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
        return Response("User coudn't find", status=404)

    else:
        current_user = User.objects.get(pk=request.user.id)
        if (not Author.objects.filter(user=current_user).exists()):
            return Response("Author coudn't find", status=404)
        else:
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

def get_friends(current_user_uuid):
    author_object = Author.objects.get(id=current_user_uuid)
    friendsDirect = Friend.objects.filter(Q(author=author_object), Q(status='Accept'))
    friendsIndirect = Friend.objects.filter(Q(friend=author_object), Q(status='Accept'))
    friends_list = []
    for friend in friendsDirect:
        if friend not in friends_list:
            friends_list.append(friend.friend)
    for friend in friendsIndirect:
        if friend not in friends_list:
            friends_list.append(friend.author)
    return friends_list

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


def is_my_friend(current_user_id, author_id):
    current_user_object = Author.objects.get(id=current_user_id)
    friend_object = Author.objects.get(id=author_id)

    relation_curUser_to_frined = Friend.objects.filter(author=current_user_object, friend=friend_object,
                                                       status="Accept")
    relation_friend_to_curUser = Friend.objects.filter(author=friend_object, friend=current_user_object,
                                                       status="Accept")

    if relation_curUser_to_frined or relation_friend_to_curUser:
        return 'true'
    else:
        return 'false'


def get_follow_status(current_user_id, author_id):
    current_user_object = Author.objects.get(id=current_user_id)
    friend_object = Author.objects.get(id=author_id)

    try:
        relation_curUser_to_friend = Friend.objects.filter(author=current_user_object,friend=friend_object)[0]
        current_status = relation_curUser_to_friend.status
        return current_status
    except:
        current_status = 'notFound'
        return current_status



def posts_list(request):
    url = "/myBlog/author/posts/?size=10"
    current_user_id = get_current_user_uuid(request)
    return render(request, 'posts.html', {"url":url, "trashable":"false",'current_user_id':current_user_id})

def new_post(request):
    return render(request, 'newpost.html')

def my_posts(request):
    url = "/myBlog/posts/mine/?size=10"
    return render(request, 'posts.html', {"url":url, "trashable":"true"})

def friend_request(request):
    return render(request,'friendrequest.html')


def my_friends(request):
    return render(request, 'myfriend.html')

def author_details(request,author_id):
    current_user_id = get_current_user_uuid(request)
    current_user_name = Author.objects.get(pk=current_user_id).displayName
    is_friend = is_my_friend(current_user_id,author_id)
    follow_status = get_follow_status(current_user_id,author_id)
    return render(request,'authordetails.html',{'authorid':author_id,'current_user_id':current_user_id,
                                                'is_friend':is_friend,'followStatus':follow_status,
                                                'current_user_name':current_user_name})
