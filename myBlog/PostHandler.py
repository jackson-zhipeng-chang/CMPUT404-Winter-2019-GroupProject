import markdown
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend, Node, RemoteUser
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework import status
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser
from . import Helpers
from uuid import UUID
import requests
from requests.auth import HTTPBasicAuth
import json
import dateutil.parser
import datetime
import time


class NewPostHandler(APIView):
    def get(self, request, format=None):
        isRemote = Helpers.check_remote_request(request)
        if isRemote:
            remoteNode = Node.objects.get(host=Helpers.get_host_from_request(request))
            remoteUser = remoteNode.nodeUser
            if remoteUser == request.user:
                posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(visibility='PUBLIC'))
                paginator = CustomPagination()
                results = paginator.paginate_queryset(posts_list, request)
                serializer=PostSerializer(results, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response("You are not using the auth node user", status=401)

        elif type(request.user) is not AnonymousUser:
            posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(visibility='PUBLIC'))
            paginator = CustomPagination()
            results = paginator.paginate_queryset(posts_list, request)
            serializer=PostSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)

        else:
            return Response("Unauthorized", status=401)


    def post(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        author = Author.objects.get(id=current_user_uuid)
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
    def post(self, request, postid, format=None):
        # this api is only for remote user.

        # step 1, POST to "requestor_host/author/requestor_id/friends/" 
        # to ensure if the friend list is correct.
        # step 2, based on step 1, query local server to see if the friends in friend list are our friend in our server.
        # step 3, based on step 2, choose one mutual friend from the list and POST TO "that_friend_host/author/that_friend_id/friends/" 
        # with requestor_host/author/requestor_id to ensure if that friend is friend of the requestor
        # step 4, if all of above three steps are true, return POST_ID post.

        if request.user.is_authenticated:
            isRemote = Helpers.check_remote_request(request)
            remote_user_uuid = Helpers.get_current_user_uuid(request)
            data = request.data
            if data["query"] == "getPost":
                sender_friend_list = data["friends"]
                # In example this is postid
                post_id = data["postid"]
                if isRemote:                   
                    print("request author id {}".format(data["author"]["id"]))
                    remoteNode = Node.objects.get(nodeUser=request.user)
                    remote_to_node = RemoteUser.objects.get(node=remoteNode)
                    if type(remote_user_uuid) is UUID:
                        postObj = Post.objects.get(pk=post_id)
                        current_author_id = postObj.author.id
                        # if the sender is post author's friend
                        for friend_url in sender_friend_list:
                            if str(current_author_id) in friend_url:
                                if not Post.objects.filter(Q(pk=postid), Q(visibility='FOAF')).exists():
                                    return Response("Post couldn't find", status=status.HTTP_404_NOT_FOUND)
                                else:
                                    post = Post.objects.get(pk=postid)
                                    serializer = PostSerializer(post)
                                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)

                        sender_url = remoteNode.host + "service/author/"+str(remote_user_uuid)
                        print('sender_url is {}'.format(sender_url))
                        if not(Author.objects.filter(id=remote_user_uuid).exists()):
                            # create a local copy for the sender
                            response = requests.get(sender_url,auth=HTTPBasicAuth(remote_to_node.remoteUsername,remote_to_node.remotePassword))
                            remoteAuthorJson = json.loads(response.content.decode('utf8').replace("'",'"'))
                            remoteAuthorObj = Helpers.get_or_create_author_if_not_exist(remoteAuthorJson)
                        # Ask sender's server if the authors in friendlist are friend with the sender
                        request_body = {
                            "query":"friends",
                            "author":sender_url,
                            "authors":sender_friend_list
                        }
                        request_url = sender_url+'/friends/'
                        header = {"Content-Type": "application/json", 'Accept': 'application/json'}
                        response = requests.post(request_url,headers=header,data = json.dumps(request_body),auth=HTTPBasicAuth(remote_to_node.remoteUsername,remote_to_node.remotePassword))
                        if response.status_code == 200:
                            remoteFriendListJson = json.loads(response.content.decode('utf8').replace("'",'"'))
                            remoteFriendList = remoteFriendListJson["authors"]
                            # step1 done
                            if len(remoteFriendList)==len(sender_friend_list):
                                # check which friends in friendlist are my friend
                                
                                my_friend_list = []
                                for friend in remoteFriendList:
                                    try:
                                        friend_id = friend.split('/')[-1]
                                    except:
                                        return Response('Wrong author id type, add host in the beginning.',status=status.HTTP_403_FORBIDDEN)
                                    if Helpers.check_two_users_friends(current_author_id,friend_id):
                                        my_friend_list.append(friend)
                                # step2 done
                                if my_friend_list:
                                    # Then it will go to at least 1 of these friend's servers and verify that they are friends of sender
                                    my_friend = my_friend_list[0]
                                    my_friend_host = my_friend.split('author')[0]
                                    friend2friend_url = my_friend+'/friends/'+sender_url.split('/')[2]+'/author/'+str(remote_user_uuid)
                                    print("friend2friend_url is {}".format(friend2friend_url))
                                    # check my_friend is from my server or remote
                                    is_local = Helpers.from_my_server(my_friend_host)
                                    if is_local:
                                        # the friend is from my server, then current author must be his friend
                                        # response FOAF post to sender
                                        if not Post.objects.filter(Q(pk=postid),Q(visibility='FOAF')).exists():
                                            return Response("Post couldn't find",status=status.HTTP_404_NOT_FOUND)
                                        else:
                                            post = Post.objects.get(pk=postid)
                                            serializer = PostSerializer(post)
                                            return JsonResponse(serializer.data,status=status.HTTP_200_OK)
                                    else:
                                        # the friend is not in my server, go to the friend's server and query
                                        my_friend_node = Node.objects.get(host=my_friend_host)
                                        my_friend_remote_user = RemoteUser.objects.get(node=my_friend_node)
                                        response = requests.get(friend2friend_url,auth=HTTPBasicAuth(my_friend_remote_user.remoteUsername,my_friend_remote_user.remotePassword))
                                        if response.status_code==200:
                                            responseJSON = json.loads(response.content.decode('utf8').replace("'", '"'))
                                            if responseJSON["friends"]:
                                                if not Post.objects.filter(Q(pk=postid), Q(visibility='FOAF')).exists():
                                                    return Response("Post couldn't find", status=status.HTTP_404_NOT_FOUND)
                                                else:
                                                    post = Post.objects.get(pk=postid)
                                                    serializer = PostSerializer(post)
                                                    return JsonResponse(serializer.data, status=status.HTTP_200_OK)
                                            else:
                                                return Response('No mutal friend',status=status.HTTP_403_FORBIDDEN)
                                        return Reponse('friend2friend api fails',status=response.status_code)
                                else:
                                    return Response('No mutual friend.',status=status.HTTP_403_FORBIDDEN)


                            else:
                                return Response('Wrong Friend List Infomation.',status=status.HTTP_403_FORBIDDEN)

                        else:
                            return Response("Responding query string is wrong.'query':'friends'.",status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response("You are not sending the request with correct format. Missing 'query':'getPost'",status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response("Unauthenticated",status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, postid, format=None):
        if (not Post.objects.filter(pk=postid).exists()):
            return Response("Post couldn't find", status=404)
        else:
            post = Post.objects.get(pk=postid)
            serializer = PostSerializer(post)
            unlisted_post = post.unlisted
            visibility = post.visibility

            if unlisted_post and visibility=='PUBLIC':
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
                    post.published=datetime.datetime.now()
                    serializer.save()
                    post.save()
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


# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django answered Sep 27 '12 at 6:17 K Z
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset answered Jul 4 '11 at 6:15 Lakshman Prasad, edited Oct 26 '13 at 2:13 Mechanical snail
# https://github.com/belatrix/BackendAllStars/blob/master/employees/views.py by Sergio Infante
# https://github.com/belatrix/BackendAllStars/blob/master/employees/serializers.py by Sergio Infante
# https://stackoverflow.com/questions/2658291/get-list-or-404-ordering-in-django answered Apr 17 '10 at 12:21 Ludwik Trammer
# https://stackoverflow.com/questions/13076822/django-dynamically-filtering-with-q-objects answered Oct 25 '12 at 20:40 Riley Watkins
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        start_time = time.time()
        if request.user.is_authenticated:
            current_user_uuid = Helpers.get_current_user_uuid(request)
            optional_Q = Q()
            if type(current_user_uuid) is UUID:
                isRemote = Helpers.check_remote_request(request)
                shareImages = True
                sharePosts = True
                my_host = Helpers.get_host_from_request(request)
                if isRemote:
                    remoteNode = Node.objects.get(nodeUser=request.user)
                    shareImages = remoteNode.shareImages
                    sharePosts = remoteNode.sharePost
                    optional_Q &= ~Q(origin__contains =remoteNode.host)
                    optional_Q &= Q(origin__contains =request.get_host())
                    if not shareImages:
                        optional_Q &= ~Q(contentType ='image/png;base64')
                        optional_Q &= ~Q(contentType ='image/jpeg;base64')

                    if not sharePosts:
                        optional_Q &= ~Q(contentType ='text/plain')
                        optional_Q &= ~Q(contentType ='text/markdown')

                    if not (Author.objects.filter(id = current_user_uuid).exists()):
                        remote_to_node = RemoteUser.objects.get(node=remoteNode)
                        authorProfileURL = remoteNode.host + "service/author/%s"%str(current_user_uuid)
                        response = requests.get(authorProfileURL, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
                        if response.status_code != 200:
                            return Response("%s is not responding"%authorProfileURL, status=404)
                        remoteAuthorJson = response.json()
                        try:
                            remoteAuthorObj = Helpers.get_or_create_author_if_not_exist(remoteAuthorJson)
                        except:
                            return Response("Author not found", status=404)
                    Helpers.update_this_friendship(remoteNode,current_user_uuid,request)
                else:
                    # if is local user, request remote server to get the post I can see
                    #---------------------------------------
                    # delete_remote_nodes_post()
                    Helpers.update_remote_friendship(current_user_uuid)
                    pull_remote_nodes(current_user_uuid,request=request)
                    #---------------------------------------

                # Helpers.update_remote_friendship(current_user_uuid)
                my_posts_list=[]
                public_posts_list = []
                friend_posts_list=[]
                private_posts_list=[]
                serveronly_posts_list=[]
                foaf_posts_list=[]

                if not isRemote:
                    if (Post.objects.filter(Q(unlisted=False), Q(author_id=current_user_uuid), optional_Q).exists()):
                        my_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=current_user_uuid), optional_Q)
                        
                if (Post.objects.filter(Q(unlisted=False), ~Q(author_id=current_user_uuid), Q(visibility='PUBLIC'), optional_Q).exists()):
                    public_posts_list = get_list_or_404(Post.objects.order_by('-published'), ~Q(author_id=current_user_uuid), Q(unlisted=False), Q(visibility='PUBLIC'), optional_Q)
                
                friends_list = Helpers.get_local_friends(current_user_uuid)
                for friend in friends_list:
                    if (Post.objects.filter(Q(unlisted=False),Q(author_id=friend.id),Q(visibility='FRIENDS'), optional_Q).exists()):
                        friend_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id), Q(visibility='FRIENDS'), optional_Q)
                    # Add FOAF post to friends as well
                    if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='FOAF'), optional_Q).exists()):
                        foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id),Q(visibility='FOAF'), optional_Q)

                    if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='PRIVATE'), optional_Q).exists()):
                        private_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id), Q(visibility='PRIVATE'), optional_Q)
                        for post in private_list:
                            if str(current_user_uuid) in post.visibleTo:
                                private_posts_list.append(post)
                    # https://stackoverflow.com/questions/22266734/django-excluding-one-queryset-from-another answered Mar 8 '14 at 8:04 Paul Draper
                                                       
                    friends_of_this_friend =  Helpers.get_friends(friend.id)
                    if request.get_host() not in friend.host:
                        remote_friends_of_this_friend = Helpers.get_remote_friends_obj_list(friend.host, friend.id)
                        friends_of_this_friend +=remote_friends_of_this_friend
                    
                    for friend_of_this_friend in friends_of_this_friend:
                        if friend_of_this_friend.id != current_user_uuid:
                            if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend_of_this_friend.id), Q(visibility='FOAF'), optional_Q).exists()):
                                foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend_of_this_friend.id),Q(visibility='FOAF'), optional_Q)
                   
                    if not isRemote:
                        if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='SERVERONLY'), optional_Q).exists()):
                            if (Helpers.get_current_user_host(current_user_uuid)==friend.host):
                                serveronly_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id),Q(visibility='SERVERONLY'), optional_Q)                        
                
                posts_list = my_posts_list+public_posts_list+friend_posts_list+private_posts_list+serveronly_posts_list+foaf_posts_list
        
                posts_list.sort(key=lambda x: x.published, reverse=True) # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects answered Dec 31 '08 at 16:42 by Triptych
                paginator = CustomPagination()
                results = paginator.paginate_queryset(posts_list, request)
                serializer=PostSerializer(results, many=True)
                print("Responsed in %s sec"%str(time.time()-start_time))
                print('reponse is {}'.format(paginator.get_paginated_response(serializer.data)))
                return paginator.get_paginated_response(serializer.data)

            else:
                public_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(visibility='PUBLIC'))
                paginator = CustomPagination()
                results = paginator.paginate_queryset(public_posts_list, request)
                serializer=PostSerializer(results, many=True)
                return paginator.get_paginated_response(serializer.data)

        else:
            return Response("Unauthorized", status=401)


# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset answered Oct 14 '13 at 13:11 Aamir Adnan
class PostToUserIDHandler(APIView):
    def get(self, request, user_id, format=None):
        if request.user.is_authenticated:
            current_user_uuid = Helpers.get_current_user_uuid(request)
            try:
                author_obj = Author.objects.get(id=user_id)
            except:
                return Response("Bad UUID format", status=400)

            if request.get_host() not in author_obj.host:
                try:
                    remoteNode = Node.objects.get(host__contains=author_obj.host)
                    remote_to_node = RemoteUser.objects.get(node=remoteNode)
                    remoteNodePostToIdURL = author_obj.host +'service/author/'+str(user_id)+'/posts/';
                    author_url = str(author_obj.host)+"service/author/"+str(current_user_uuid)
                    headers = {"X-UUID": str(current_user_uuid), "X-Request-User-ID": author_url}
                    print("Pulling: %s"%remoteNodePostToIdURL)
                    response = requests.get(remoteNodePostToIdURL,headers=headers, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
                    if response.status_code == 200: 
                        return response
                except Exception as e:
                    print("an error occured when pulling remote posts: %s"%e)
                    pass

            if type(current_user_uuid) is UUID:
                optional_Q = Q()
                isRemote = Helpers.check_remote_request(request)
                shareImages = True
                sharePosts = True

                if isRemote:
                    remoteNode = Node.objects.get(nodeUser=request.user)
                    shareImages = remoteNode.shareImages
                    sharePosts = remoteNode.sharePost
                    optional_Q &= ~Q(origin__contains =remoteNode.host)
                    optional_Q &= Q(origin__contains =request.get_host())
                    if not shareImages:
                        optional_Q &= ~Q(contentType ='image/png;base64')
                        optional_Q &= ~Q(contentType ='image/jpeg;base64')

                    if not sharePosts:
                        optional_Q &= ~Q(contentType ='text/plain')
                        optional_Q &= ~Q(contentType ='text/markdown')

                    if not (Author.objects.filter(id = current_user_uuid).exists()):
                        remote_to_node = RemoteUser.objects.get(node=remoteNode)
                        authorProfileURL = remoteNode.host + "service/author/%s"%str(current_user_uuid)
                        response = requests.get(authorProfileURL, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
                        if response.status_code != 200:
                            return Response("%s is not responding"%authorProfileURL, status=404)

                        remoteAuthorJson = response.json()
                        try:
                            remoteAuthorObj = Helpers.get_or_create_author_if_not_exist(remoteAuthorJson)
                        except:
                            return Response("Author not found", status=404)
                    
                    Helpers.update_this_friendship(remoteNode,current_user_uuid,request)
                else:
                    pull_remote_nodes(current_user_uuid,request=request)


                public_posts_list=[]
                friend_posts_list=[]
                private_posts_list=[]
                serveronly_posts_list=[]
                foaf_posts_list=[]
                if (Post.objects.filter(Q(unlisted=False), Q(author_id=user_id),Q(visibility='PUBLIC'), optional_Q).exists()):
                    public_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id),Q(visibility='PUBLIC'), optional_Q)

                isFriend = Helpers.check_two_users_friends(current_user_uuid, user_id)
                isFoaf = False

                friends_of_this_author = Helpers.get_friends(user_id)
                my_friends = Helpers.get_friends(current_user_uuid)
                print("my_friends: %s"%str(my_friends))
                print("friends_of_this_author: %s"%str(friends_of_this_author))
                for friend_of_this_author in friends_of_this_author:
                    if friend_of_this_author in my_friends:
                        isFoaf = True
                        break
                
                if not isFriend and isFoaf and (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id),Q(visibility='FOAF'), optional_Q).exists()):
                    foaf_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id),Q(visibility='FOAF'), optional_Q)

                if isFriend:
                    if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id),Q(visibility='FRIENDS'), optional_Q).exists()):
                        friend_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='FRIENDS'), optional_Q)

                    if (Post.objects.filter(Q(unlisted=False), Q(author_id=user_id), Q(visibility='FOAF'), optional_Q).exists()):
                        foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id),Q(visibility='FOAF'), optional_Q)

                    if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id), Q(visibility='PRIVATE'), optional_Q).exists()):
                        private_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='PRIVATE'), optional_Q)
                        for post in private_list:
                            if str(current_user_uuid) in post.visibleTo:
                                private_posts_list.append(post)

                    if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id), Q(visibility='SERVERONLY'), optional_Q).exists()):
                        user_host = Author.objects.get(id=user_id).host
                        if (Helpers.get_current_user_host(current_user_uuid)==user_host):
                            serveronly_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='SERVERONLY'), optional_Q)


                posts_list = public_posts_list+friend_posts_list+private_posts_list+serveronly_posts_list+foaf_posts_list
                posts_list.sort(key=lambda x: x.published, reverse=True)
                paginator = CustomPagination()
                results = paginator.paginate_queryset(posts_list, request)
                serializer=PostSerializer(results, many=True)
                return paginator.get_paginated_response(serializer.data)

            else:
                public_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id), Q(visibility='PUBLIC'))
                paginator = CustomPagination()
                results = paginator.paginate_queryset(public_posts_list, request)
                serializer=PostSerializer(results, many=True)
                return paginator.get_paginated_response(serializer.data)

        else:
            return Response("Unauthorized", status=401)


# For local using only
class MyPostHandler(APIView):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            current_user_uuid = Helpers.get_current_user_uuid(request)
            if type(current_user_uuid) == UUID:
                posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=current_user_uuid))
                paginator = CustomPagination()
                results = paginator.paginate_queryset(posts_list, request)
                serializer=PostSerializer(results, many=True)
                return paginator.get_paginated_response(serializer.data)
            else:
                return Response("Unauthorized", status=401)
        else:
            return Response("Unauthorized", status=401)


def pull_remote_nodes(current_user_uuid,request=None):
    all_nodes = Node.objects.all()
    current_user_host = Helpers.get_current_user_host(current_user_uuid)
    for node in all_nodes:
        nodeURL = node.host+"author/posts/"
        author_url = str(current_user_host)+"service/author/"+str(current_user_uuid)
        headers = {"X-UUID": str(current_user_uuid), "X-Request-User-ID": author_url}
        # http://docs.python-requests.org/en/master/user/authentication/ ©MMXVIII. A Kenneth Reitz Project.
        remote_to_node = RemoteUser.objects.get(node=node)

        try:
            # https://stackoverflow.com/questions/12737740/python-requests-and-persistent-sessions answered Oct 5 '12 at 0:24
            print("Pulling: %s"%nodeURL)
            response = requests.get(nodeURL,headers=headers, auth=HTTPBasicAuth(remote_to_node.remoteUsername, remote_to_node.remotePassword))
            print(response.status_code)
        except Exception as e:
            print("an error occured when pulling remote posts: %s"%e)
            continue

        if response.status_code == 200:
            postJson = response.json()
            remote_postid_set = set()
            if int(postJson["count"]) != 0:    
                for post in postJson["posts"]:              
                    #  if the post is already in our db and published date did not change, do nothing
                    #  if the postid is not in our db, add
                    #  if the postid from our db does not exist in response, delete.
                    #  if the post's published time changed, delete this post locally and add the new one.

                    remotePostID = post['id']
                    remote_postid_set.add(remotePostID)
                    remotePostPublished = post["published"]

                    # if the post in our db has been changed, delete
                    if Post.objects.filter(Q(postid=remotePostID),~Q(published=remotePostPublished)).exists():
                        print("Updating posts: %s"%post["title"])
                        Post.objects.filter(Q(postid=remotePostID),~Q(published=remotePostPublished)).delete()
            
                    remoteAuthorJson = post["author"]
                    remoteAuthorObj = Helpers.get_or_create_author_if_not_exist(remoteAuthorJson)

                    if not Post.objects.filter(postid=post["id"]).exists():
                        print("Creating posts: %s"%post["title"])
                        if (post["contentType"] == "text/markdown"):
                            post["content"] = markdown.markdown(post["content"])
                        remotePostObj = Post.objects.create(postid=post["id"], title=post["title"],source=node.host+"service/posts/"+post["id"], 
                            origin=post["origin"], content=post["content"],categories=post["categories"], 
                            contentType=post["contentType"], author=remoteAuthorObj,visibility=post["visibility"], 
                            visibleTo=post["visibleTo"], description=post["description"],
                            unlisted=post["unlisted"])
                        #https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object community wiki 5 revs, 4 users 81% Wes Winham
                        publishedObj = dateutil.parser.parse(post["published"])
                        remotePostObj.published = publishedObj
                        remotePostObj.save()

                    if len(post["comments"]) != 0:
                        for comment in post["comments"]:
                            remotePostCommentAuthorJson = comment["author"]
                            if len(remotePostCommentAuthorJson) != 0:
                                remotePostCommentAuthorObj = Helpers.get_or_create_author_if_not_exist(remotePostCommentAuthorJson)
                                if not Comment.objects.filter(id=comment["id"]).exists():
                                    remotePostCommentObj = Comment.objects.create(id=comment["id"], postid=post["id"],
                                    author = remotePostCommentAuthorObj, comment=comment["comment"],contentType='text/plain')
                                    commentPublishedObj = dateutil.parser.parse(comment["published"])
                                    remotePostCommentObj.published = commentPublishedObj
                                    remotePostCommentObj.save()

                # this part is for filtering the post not in remote posts, which means the post has been deleted in remote server
                remote_host = node.host
                print("Filtering posts for %s"%remote_host)
                all_remote_post_id = Post.objects.filter(Q(source__contains=remote_host)).values_list("postid",flat=True)
                print("all_remote_post_id %s"%str(all_remote_post_id))
                # all_remote_post_id_set is a set of remote postsid in our server
                # remote_postid_set is the remote postid visible to me from other server
                print("remote_postid_set %s"%str(remote_postid_set))
                if len(all_remote_post_id) != len(remote_postid_set):
                    all_remote_post_id_set = set()
                    for post_id in all_remote_post_id:
                        all_remote_post_id_set.add(str(post_id))
                    print("all_remote_post_id_set %s"%str(all_remote_post_id_set))
                    deleted_post_id = all_remote_post_id_set-remote_postid_set
                    print("deleted_post_id %s"%str(deleted_post_id))
                    for post_id in deleted_post_id:
                        Post.objects.filter(postid=post_id).delete()
