from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Author, Comment, Friend, Node, RemoteUser
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User, AnonymousUser
from django.views import generic
from django.db.models import Q
from django.shortcuts import render
from uuid import UUID
from django.http import HttpResponse, HttpResponseNotFound, Http404
import requests
from requests.auth import HTTPBasicAuth
import json
import re
import datetime

def get_author_or_not_exits(current_user_uuid):
    if type(current_user_uuid) != UUID:
        current_user_uuid = UUID(current_user_uuid)
    try:
        Author.objects.filter(id=current_user_uuid)
        return Author.objects.get(id=current_user_uuid)
    except:
        return False


def get_host_from_request(request):
# https://docs.djangoproject.com/en/2.1/ref/request-response/
    host = request.scheme+"://"+request.get_host()+"/"
    return host

def get_current_user_uuid(request):
    isRemote = check_remote_request(request)
    if isRemote:
        try:
            return UUID(request.META["HTTP_X_UUID"])
        except:
            return  Response("Author UUID couldn't find", status=404)
    else:
        if (not User.objects.filter(pk=request.user.id).exists()):
            return Response("User coudn't find", status=404)
        else:
            current_user = User.objects.get(pk=request.user.id)
            if (not Author.objects.filter(user=current_user).exists()):
                return Response("Author couldn't find", status=404)
            else:
                author = get_object_or_404(Author, user=current_user)
                return author.id

def get_current_user_host(current_user_uuid):
    if (not Author.objects.filter(id=current_user_uuid).exists()):
        return Author.objects.get(id=current_user_uuid).host

def verify_current_user_to_post(post, request):
    post_visibility = post.visibility
    post_author = post.author_id
    unlisted_post = post.unlisted
    if request.user.is_authenticated:
    #if User.objects.filter(pk=request.user.id).exists():
        current_user_uuid = get_current_user_uuid(request)
        isFriend = check_two_users_friends(post_author,current_user_uuid)
        if current_user_uuid == post_author:
            return True
        else:
            if post_visibility == 'PUBLIC':
                return True
            elif post_visibility == 'FOAF':
                return True
            elif post_visibility == 'FRIENDS':
                if isFriend:
                    return True
                else:
                    return False
            elif post_visibility == 'PRIVATE':
                if current_user_uuid == post_author:
                    return True
                elif post.visibleTo is not None:
                    if (str(current_user_uuid) in post.visibleTo):
                        return True
                    else:
                        return False
                else:
                    return False
            elif post_visibility == 'SERVERONLY' and isFriend:
                post_server = Author.objects.get(id=post.author.id).host
                user_server = Author.objects.get(id=current_user_uuid).host
                if user_server == post_server:
                    return True
                else:
                    return False
            else:
                    return False
    elif (not User.objects.filter(pk=request.user.id).exists()):
        return False
        
def get_friends(current_user_uuid):
    update_remote_friendship(current_user_uuid)
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

def get_uuid_from_url(url):
    uuid = url.split("/service/author/")
    return UUID(uuid[1])

def get_local_friends(current_user_uuid):
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

def update_remote_friendship(current_user_uuid):
    local_friends_list = get_local_friends(current_user_uuid)
    for node in Node.objects.all():
        friendshipURL = node.host+"service/author/"+str(current_user_uuid)+"/friends/"
        try:
            remote_to_node = RemoteUser.objects.get(node=node)
            response = requests.get(friendshipURL, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
            data = json.loads(response.content.decode('utf8').replace("'", '"'))
            remoteFriendsURL = data["authors"]
            remote_friends_uuid_list = convert_url_list_to_uuid(remoteFriendsURL)

            if len(remoteFriendsURL) != 0:
                for remoteFriend_uuid in remote_friends_uuid_list:
                    isFollowing = check_author1_follow_author2(current_user_uuid,remoteFriend_uuid)
                    if isFollowing:
                        update_friendship_obj(current_user_uuid, remoteFriend_uuid, 'Accept')

            if len(local_friends_list) != 0:
                for localFriend in local_friends_list:
                    if (localFriend.id not in remote_friends_uuid_list):
                        if (Friend.objects.filter(Q(author=localFriend.id), Q(status='Accept')).exists()):
                            friendship = Friend.objects.get(Q(author=localFriend.id), Q(status='Accept'))
                            last_modified_time = friendship.last_modified_time.replace(tzinfo=None)
                            if ((datetime.datetime.utcnow() - last_modified_time).total_seconds () > 30):
                                friendship.delete()

                        if (Friend.objects.filter(Q(friend=localFriend.id), Q(status='Accept')).exists()):
                            friendship = Friend.objects.get(Q(friend=localFriend.id), Q(status='Accept'))
                            last_modified_time = friendship.last_modified_time.replace(tzinfo=None)
                            if ((datetime.datetime.utcnow() - last_modified_time).total_seconds () > 30):
                                friendship.delete()
        except:
            pass

def convert_url_list_to_uuid(friends_list):
    new_list = []
    for author_url in friends_list:
        uuid = get_uuid_from_url(author_url)
        new_list.append(uuid)
    return new_list


def update_friendship_obj(author, friend, newstatus):
    try:
        friendrequests = Friend.objects.get(author=author, friend=friend)
        friendrequests.status=newstatus
        friendrequests.save()
    except:
        pass

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

def home(request):
    current_user_uuid = get_current_user_uuid(request)
    if type(current_user_uuid) == UUID:
        user_author = Author.objects.get(id=current_user_uuid)
        author_github = user_author.github
        if author_github is not None:
            github_id = author_github.replace("https://github.com/","").replace("/","")
            github_url = "https://api.github.com/users/%s/events/public"%github_id
        else:
            github_url = "null"
        posts_url = "/service/author/posts/?size=10"
        displayName = user_author.displayName
        user_github = user_author.github
        return render(request, 'homepage.html', {"posts_url":posts_url, "github_url":github_url, "trashable":"false",
                                                 'displayName':displayName,'user_id':current_user_uuid,'user_github':user_github})
    else:
        return render(request, 'homepage.html')

def is_my_friend(current_user_id, author_id):
    current_user_object = Author.objects.get(id=current_user_id)
    if type(current_user_id) is UUID:
        friend_object = get_object_or_404(Author, id=author_id)
        relation_curUser_to_frined = Friend.objects.filter(author=current_user_object, friend=friend_object,status="Accept")
        relation_friend_to_curUser = Friend.objects.filter(author=friend_object, friend=current_user_object,status="Accept")
        if relation_curUser_to_frined or relation_friend_to_curUser:
            return 'true'
        else:
            return 'false'
    else:
        raise Response("User coudn't find", status=404)
        
def get_follow_status(current_user_id, author_id):
    current_user_object = Author.objects.get(id=current_user_id)
    if type(current_user_id) is UUID:
        friend_object = Author.objects.get(id=author_id)
        try:
            relation_curUser_to_friend = Friend.objects.filter(author=current_user_object,friend=friend_object)[0]
            current_status = relation_curUser_to_friend.status
            return current_status
        except:
            current_status = 'notFound'
            return current_status
    else:
        raise Response("User coudn't find", status=404)

def check_remote_request(request):
    if type(request.user) is not AnonymousUser:
        if (Node.objects.filter(nodeUser=request.user).exists()):
            return True
        else:
            return False
    else:
        return False

def get_or_create_author_if_not_exist(author_json):
    AuthorObj = get_author_or_not_exits(author_json['id'])
    if AuthorObj is False:
        if User.objects.filter(username=author_json["displayName"]).exists():
            userObj = User.objects.get(username=author_json["displayName"])
        else:
            userObj = User.objects.create_user(username=author_json["displayName"],password="password", is_active=False)
        host = author_json["host"]
        host = host.replace("localhost", "127.0.0.1")
        author = Author.objects.create(id=author_json['id'], displayName=author_json["displayName"],user=userObj, host=host)
        author.save()
        AuthorObj = author

    return AuthorObj

#-----------------------------------------Local endpoints-----------------------------------------#
def new_post(request):
    return render(request, 'newpost.html')

def my_posts(request):
    posts_url = "/service/posts/mine/?size=10"
    current_user_id = get_current_user_uuid(request)
    current_user = Author.objects.get(pk=current_user_id)
    current_user_name = current_user.displayName
    current_user_github = current_user.github
    return render(request, 'my_posts_list.html', {"posts_url":posts_url, "trashable":"true","user_id":current_user_id,
                "displayName":current_user_name,"user_github":current_user_github})

def friend_request(request):
    return render(request,'friendrequest.html')

def my_friends(request):
    return render(request, 'myfriends.html')

def my_profile(request):
    return render(request, 'myprofile.html')

def author_details(request,author_id):
    get_author_or_not_exits(author_id)
    current_user_id = get_current_user_uuid(request)
    if type(current_user_id) is UUID:
        current_user_name = Author.objects.get(pk=current_user_id).displayName
        current_user_github = Author.objects.get(pk=current_user_id).github
        is_friend = is_my_friend(current_user_id,author_id)
        follow_status = get_follow_status(current_user_id,author_id)
        friend = Author.objects.get(pk=author_id)
        host = friend.host
        url = friend.host + 'service/author/' + author_id
        friend_name = friend.displayName
        friend_github = friend.github
        return render(request,'authordetails.html',{'authorid':author_id,'current_user_id':current_user_id,
                                                    'is_friend':is_friend,'followStatus':follow_status,
                                                    'current_user_name':current_user_name,'friend_host':host,
                                                    'friend_url':url,'friend_name':friend_name,
                                                    'friend_github':friend_github,'current_user_github':current_user_github})
    else:
        return render(request, 'homepage.html')


def post_details(request, post_id):
    comments = Comment.objects.filter(postid=post_id)
    post = Post.objects.get(pk=post_id)
    arr = post.origin.split("/")
    post_host = arr[0]+"//"+arr[2]+'/'
    accessible = verify_current_user_to_post(post, request)
    if accessible:
        if post.contentType == "image/png;base64" or post.contentType == "image/jpeg;base64":
            content_is_picture = True
        else:
            content_is_picture = False

        current_author_id = get_current_user_uuid(request)
        if type(current_author_id) is UUID:
            current_display_name = Author.objects.get(pk=current_author_id).displayName
            current_user_github = Author.objects.get(pk=current_author_id).github
            if (post.author.displayName == current_display_name):
                current_author_is_owner = True
            else:
                current_author_is_owner = False

            categories = []
            partially_split_categories = post.categories.split(" ")
            for partially_split_category in partially_split_categories:
                categories += partially_split_category.split(",")

            text_area_id = "commentInput"+post_id

            return render(request, 'postdetails.html', {'author': post.author, 'title': post.title,
                                                        'description': post.description, 'categories': categories,
                                                        'unlisted': post.unlisted,
                                                        'content': post.content, 'visibility': post.visibility,
                                                        'published': post.published, 'comments': comments,
                                                        "contentIsPicture": content_is_picture, 'postID': post.postid,
                                                        "currentAuthorIsOwner": current_author_is_owner,
                                                        "textAreaID": text_area_id,"current_user_id":current_author_id,
                                                        "current_user_name":current_display_name,"current_user_github":current_user_github,
                                                        "post_host":post_host})
        else:
            return render(request, 'homepage.html')
    else:
        raise Http404("Post does not exist")


def edit_post(request, post_id):
    comments = Comment.objects.filter(postid=post_id)
    post = Post.objects.get(pk=post_id)
    accessible = verify_current_user_to_post(post, request)
    if accessible:

        current_author_id = get_current_user_uuid(request)
        if type(current_author_id) is UUID:
            current_display_name = Author.objects.get(pk=current_author_id).displayName
            if post.author.displayName == current_display_name:
                current_author_is_owner = True
            else:
                current_author_is_owner = False

            text_area_id = "commentInput" + post_id

            visible_to_names = []
            visible_to_ids = []

            if post.visibleTo != 'null':
                for visible_to in post.visibleTo.split(","):
                    visible_to_names.append(Author.objects.get(pk=visible_to).displayName)
                    visible_to_ids.append(Author.objects.get(pk=visible_to).id.urn.replace("urn:uuid:", ""))

            return render(request, 'editpost.html', {'author': post.author, 'title': post.title,
                                                        'description': post.description, 'categories': post.categories,
                                                        'unlisted': post.unlisted,
                                                        'content': post.content, 'visibility': post.visibility,
                                                        'published': post.published, 'comments': comments,
                                                        "contentType": post.contentType, 'postID': post.postid,
                                                        "textAreaID": text_area_id,
                                                        "visibleToNames": visible_to_names,
                                                        "visibleToIDs": visible_to_ids
                                                     })
        else:
            return render(request, 'homepage.html')
    else:
        raise Http404("Post does not exist")



# People available to show
# file

# Very slow loading picture content
# pressing change button must make changes
# change new_post_helper to post_editor_helper?