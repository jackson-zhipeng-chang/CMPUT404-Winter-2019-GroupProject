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
import dateutil.parser
import time

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
    if request.user.is_authenticated:
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
    # if (not Author.objects.filter(id=current_user_uuid).exists()):
    #     return Author.objects.get(id=current_user_uuid).host
    try:
        return Author.objects.get(id=current_user_uuid).host
    except:
        return None

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
    uuid = url.split("/author/")
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
            if response.status_code != 200:
                return Response("%s is not responding"%friendshipURL, status=404)
                
            data = response.json()
            remoteFriendsURL = data["authors"]
            remote_friends_uuid_list = convert_url_list_to_uuid(remoteFriendsURL)
            print("remote_friends_uuid_list is {}:".format(remote_friends_uuid_list))
            print("local_friends_list is {}:".format(local_friends_list))
            if len(remoteFriendsURL) != 0:
                for remoteFriend_uuid in remote_friends_uuid_list:
                    isFollowing = check_author1_follow_author2(current_user_uuid,remoteFriend_uuid)
                    if isFollowing:
                        print('Changing Status to accept for author %s and %s'%(current_user_uuid, remoteFriend_uuid))
                        update_friendship_obj(current_user_uuid, remoteFriend_uuid, 'Accept')
            if len(local_friends_list) != 0:
                for localFriend in local_friends_list:
                    if Friend.objects.filter(Q(author=localFriend.id),Q(status='Accept')).exists():
                        friendship_of_local_friend = Friend.objects.get(Q(author=localFriend.id),Q(status='Accept'))
                        remote_friend_of_local_friend = friendship_of_local_friend.friend
                    elif Friend.objects.filter(Q(friend=localFriend.id),Q(status='Accept')).exists():
                        friendship_of_local_friend = Friend.objects.get(Q(friend=localFriend.id),Q(status='Accept'))
                        remote_friend_of_local_friend = friendship_of_local_friend.author
                        print("debugging")
                        print(localFriend.id)
                        print(remote_friends_uuid_list)
                        print(node.host)
                        print(remote_friend_of_local_friend.host)

                    if (localFriend.id not in remote_friends_uuid_list) and (node.host == remote_friend_of_local_friend.host):
                        print("deleting friendship %s"%str(friendship_of_local_friend))
                        friendship_of_local_friend.delete()
                        print("done")
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
    if (Author.objects.filter(id=author1_id).exists()) and (Author.objects.filter(id=author2_id).exists()):
        author1_object = Author.objects.get(id=author1_id)
        author2_object = Author.objects.get(id=author2_id)
        friend1To2 = Friend.objects.filter(author=author1_object, friend=author2_object, status="Accept").exists()
        friend2To1 = Friend.objects.filter(author=author2_object, friend=author1_object, status="Accept").exists()
        if friend1To2 or friend2To1:
            return True
        else:
            return False
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
    if 'author/' in author_json['id']:
        author_id = author_json['id'].split('author/')[1]
        try:
            author_id = UUID(author_id)
        except:
            print("Author/Friend id in bad format")
    else:
        try:
            author_id = UUID(author_json['id'])
        except:
            print("Author/Friend id in bad format")

    AuthorObj = get_author_or_not_exits(author_id)
    if AuthorObj is False:
        if User.objects.filter(username=author_json["displayName"]).exists():
            userObj = User.objects.get(username=author_json["displayName"])
        else:
            userObj = User.objects.create_user(username=author_json["displayName"],password="password", is_active=False)
        host = author_json["host"]
        host = host.replace("localhost", "127.0.0.1")
        author = Author.objects.create(id=author_id, displayName=author_json["displayName"],user=userObj, host=host)
        author.save()
        AuthorObj = author

    return AuthorObj

def verify_remote_author(author_json):
    author_hot = author_json["host"]
    profile_url = author_hot+"service/author/"+str(author_json["id"])
    try:
        respons = requests.get(profile_url)
        if respons.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def send_FR_to_remote(nodeObj,data):
    URL = nodeObj.host + 'service/friendrequest/'
    header = {"Content-Type": "application/json", 'Accept': 'application/json'}
    remote_server = RemoteUser.objects.get(node=nodeObj)
    data = json.dumps(data)
    response = requests.post(URL, headers=header, data=data,
                             auth=HTTPBasicAuth(remote_server.remoteUsername,
                                                remote_server.remotePassword))
    # if response.status_code == 200:

    #     return Response("friend request sent", status=status.HTTP_200_OK)
    # else:
    #     return Response("Something went wrong", status=response.status_code)
    return response.status_code

def from_my_server(host):
    for node in Node.objects.all():
        if str(node.host) in str(host):
            return False
    return True

def pull_remote_posts(current_user_uuid):
    remotePostList = []
    all_nodes = Node.objects.all()
    for node in all_nodes:
        nodeURL = node.host+'service/author/posts'
        headers = {"X-UUID":str(current_user_uuid)}
        # http://docs.python-requests.org/en/master/user/authentication/ ©MMXVIII. A Kenneth Reitz Project.
        remote_to_node = RemoteUser.objects.get(node=node)
        try:
            response = requests.get(nodeURL,headers=headers,auth=HTTPBasicAuth(remote_to_node.remoteUsername,remote_to_node.remotePassword))
            print('type of response is {}'.format(type(response)))
        except Exception as e:
            print("an error occured when pulling remote posts: %s"%e)
            continue
        
        if response.status_code == 200:
            postJson = response.json()
            remotePostList += postJson['posts']
    return remotePostList

def get_remote_friends_obj_list(remote_host, remote_user_uuid):
    request_url = remote_host + "service/author/"+str(remote_user_uuid)+"/friends/"
    headers = {"Accept": 'application/json'}
    try:
        remoteNode = Node.objects.get(host__contains=remote_host)
        remote_to_node = RemoteUser.objects.get(node=remoteNode)
        response = requests.get(request_url,headers=headers,auth=HTTPBasicAuth(remote_to_node.remoteUsername,remote_to_node.remotePassword))
    except Exception as e:
        print("Something wring when pull remote friend list %s"%e)
        return []

    if response.status_code == 200:
        remote_friend_obj_list = []
        data = response.json()
        author_list = data["authors"]
        if len(author_list) != 0:
            for author_url in author_list:
                response = requests.get(author_url)
                remoteAuthorJson = response.json()
                remoteAuthorObj = get_or_create_author_if_not_exist(remoteAuthorJson)
                remote_friend_obj_list.append(remoteAuthorObj)
        return remote_friend_obj_list
    else:
        return []
   

def update_this_friendship(remoteNode,remote_user_uuid,request):
    remote_authorObj = Author.objects.get(pk=remote_user_uuid)
    remote_host = remoteNode.host
    remote_to_node = RemoteUser.objects.get(node=remoteNode)
    local_friend_list_of_remote_user = []
    # local_friends_obj_list = list(Friend.objects.filter(Q(author=remote_authorObj)|Q(friend=remote_authorObj)))
    if Friend.objects.filter(author=remote_authorObj).exists():
        local_friend_list_of_remote_user += [friend.friend.host+"author/"+str(friend.friend.id) for friend in list(Friend.objects.filter(author=remote_authorObj))]
    if Friend.objects.filter(friend=remote_authorObj).exists():
        local_friend_list_of_remote_user += [friend.author.host+"author/"+str(friend.author.id) for friend in list(Friend.objects.filter(friend=remote_authorObj))]


    if local_friend_list_of_remote_user:
        # local_friend_list_of_remote_user = [str(friend.id) for friend in local_friends_obj_list]
        request_body = {
            "query":"friends",
            "author":remote_host + "service/author/"+str(remote_user_uuid),
            "authors":local_friend_list_of_remote_user
        }
        #Get friend list of this author
        request_url = remote_host + "service/author/"+str(remote_user_uuid)+"/friends/"
        headers = {"Content-Type": 'application/json', "Accept": 'application/json'}
        data = json.dumps(request_body)
        response = requests.post(request_url,headers=headers,data=data,auth=HTTPBasicAuth(remote_to_node.remoteUsername,remote_to_node.remotePassword))
        print(response.content)
        if response.status_code == 200:
            response_friendlist_set = set(response.json()["authors"])
            local_friend_set = set(local_friend_list_of_remote_user)
            extra_friend = local_friend_set - response_friendlist_set
            print('extra_friend {}'.format(extra_friend))
            my_host = request.get_host()
            print('my host is {}'.format(my_host))
            try:
                for friend_url in extra_friend:
                    # TODO: get friend's host in smart way
                    friend_uuid=friend_url.replace('https://'+my_host+'/author/',"")
                    friend_obj = Author.objects.get(Q(pk=friend_uuid))
                    if Friend.objects.filter(Q(author=friend_obj),Q(status="Accept")).exists():
                        Friend.objects.get(Q(author=friend_obj),Q(status="Accept")).delete()
                    if Friend.objects.filter(Q(friend=friend_obj),Q(status="Accept")).exists():
                        Friend.objects.get(Q(friend=friend_obj),Q(status="Accept")).delete()

            except Exception as e:
                print("an error occured: %s"%e)

        else:
            print("Something wrong ",response.status_code)            
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
        update_remote_friendship(current_user_id)
        is_friend = is_my_friend(current_user_id,author_id)
        follow_status = get_follow_status(current_user_id,author_id)
        friend = Author.objects.get(pk=author_id)
        host = friend.host
        url = friend.host + 'service/author/' + str(author_id)
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
    current_user_uuid = get_current_user_uuid(request)
    if type(post_id) is UUID:   
        if Post.objects.filter(pk=post_id).exists():
            post = Post.objects.get(pk=post_id)
        else:
            for node in Node.objects.all():
                nodeURL = node.host+"service/posts/%s"%post_id
                headers = {"X-UUID": str(current_user_uuid)}
                # http://docs.python-requests.org/en/master/user/authentication/ ©MMXVIII. A Kenneth Reitz Project.
                remote_to_node = RemoteUser.objects.get(node=node)
                # https://stackoverflow.com/questions/12737740/python-requests-and-persistent-sessions answered Oct 5 '12 at 0:24
                response = requests.get(nodeURL,headers=headers, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
                if response.status_code == 200:
                    postJson = response.json()
                    remoteAuthorJson = postJson["author"]
                    try:
                        remoteAuthorObj = get_or_create_author_if_not_exist(remoteAuthorJson)
                    except:
                        raise Http404("Author does not exist")
                    # Create the post object for final list
                    if not Post.objects.filter(postid=postJson["id"]).exists():
                        post = Post.objects.create(postid=postJson["id"], title=postJson["title"],source=node.host+"service/posts/"+postJson["id"], 
                            origin=postJson["origin"], content=postJson["content"],categories=postJson["categories"], 
                            contentType=postJson["contentType"], author=remoteAuthorObj,visibility=postJson["visibility"], 
                            visibleTo=postJson["visibleTo"], description=postJson["description"],
                            unlisted=postJson["unlisted"])
                            #https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object community wiki 5 revs, 4 users 81% Wes Winham
                        publishedObj = dateutil.parser.parse(postJson["published"])
                        post.published = publishedObj
                        post.save()
                        if len(postJson["comments"]) != 0:
                            for j in range (0, len(postJson["comments"])):
                                remotePostCommentAuthorJson = postJson["comments"][j]["author"]
                                remotePostCommentAuthorObj = get_or_create_author_if_not_exist(remotePostCommentAuthorJson)
                                remotePostCommentObj = Comment.objects.create(id=postJson["comments"][j]["id"], postid=postJson["comments"][j]["id"],
                                author = remotePostCommentAuthorObj, comment=postJson["comments"][j]["comment"],contentType=postJson["comments"][j]["contentType"])
                                commentPublishedObj = dateutil.parser.parse(postJson["comments"][j]["published"])
                            remotePostCommentObj.published = commentPublishedObj
                            remotePostCommentObj.save()

        if not Post.objects.filter(pk=post_id).exists():
            raise Http404("Post does not exist")

        else:
            comments = Comment.objects.filter(postid=post_id)
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

                    text_area_id = "commentInput"+str(post_id)

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

            text_area_id = "commentInput" + str(post_id)

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

