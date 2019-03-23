import markdown
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render,get_list_or_404
from .models import Post, Author, Comment, Friend, Node
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer, CustomPagination, FriendSerializer
from rest_framework import status
from django.contrib.auth.models import User, AnonymousUser
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from rest_framework.parsers import JSONParser, MultiPartParser
from . import Helpers
from uuid import UUID
import requests
import json
import dateutil.parser


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
        '''
        # This is needed for FOAF calls, it asks the other server to decide to send us a
        # post or not based on friends.
        # one of Greg's friends has to be be LARA's friend

        # Here GREG tries to get a post from LARA that's marked as FOAF visibility
        # the server will query greg's server to ensure that he is friends with 7de and 11c
        # then it will get the users from its own server and see if they are friends of Lara
        # Then it will go to at least 1 of these friend's servers and verify that they are friends of Greg
        # once it is verified via the 3 hosts that Greg is a friend, then greg will get the data for lara's post
        # POST to http://service/posts/{POST_ID} , sending the body

        {
            "query":"getPost",
            "postid":"{POST_ID}",
            "url":"http://service/posts/{POST_ID}",
            "author":{ # requestor
                # UUID
                "id":"http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
                "host":"http://127.0.0.1:5454/",
                "displayName":"Jerry Johnson",
                # url to the authors information
                "url":"http://127.0.0.1:5454/author/de305d54-75b4-431b-adb2-eb6b9e546013",
                # HATEOS
                "github": "http://github.com/jjohnson"
            },
            # friends of author
            "friends":[
                "http://127.0.0.1:5454/author/7deee0684811f22b384ccb5991b2ca7e78abacde",
                "http://127.0.0.1:5454/author/11c3783f15f7ade03430303573098f0d4d20797b",
            ]
        }
        # then this returns with the generic GET http://service/posts/{POST_ID}
        '''
        
        return JsonResponse(status=200)

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


# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django answered Sep 27 '12 at 6:17 K Z
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset answered Jul 4 '11 at 6:15 Lakshman Prasad, edited Oct 26 '13 at 2:13 Mechanical snail
# https://github.com/belatrix/BackendAllStars/blob/master/employees/views.py by Sergio Infante
# https://github.com/belatrix/BackendAllStars/blob/master/employees/serializers.py by Sergio Infante
# https://stackoverflow.com/questions/2658291/get-list-or-404-ordering-in-django answered Apr 17 '10 at 12:21 Ludwik Trammer
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        isRemote = Helpers.check_remote_request(request)
        if isRemote:
            current_user_uuid = UUID(request.query_params['author_uuid'])
        else:
            current_user_uuid = Helpers.get_current_user_uuid(request)

        if type(current_user_uuid) == UUID:
            my_posts_list=[]
            public_posts_list = []
            friend_posts_list=[]  
            private_posts_list=[]
            serveronly_posts_list=[]
            foaf_posts_list=[]
            remotePosts = []

            if (Post.objects.filter(Q(unlisted=False), Q(author_id=current_user_uuid)).exists()):
                my_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=current_user_uuid))

            if (Post.objects.filter(Q(unlisted=False), ~Q(author_id=current_user_uuid), Q(visibility='PUBLIC')).exists()):
                public_posts_list = get_list_or_404(Post.objects.order_by('-published'), ~Q(author_id=current_user_uuid), Q(unlisted=False), Q(visibility='PUBLIC'))

            friends_list = Helpers.get_friends(current_user_uuid)
            for friend in friends_list:
                if (Post.objects.filter(Q(unlisted=False),Q(author_id=friend.id),Q(visibility='FRIENDS')).exists()):
                    friend_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id), Q(visibility='FRIENDS'))
                # Add FOAF post to friends as well
                if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='FOAF')).exists()):
                    foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id),Q(visibility='FOAF'))

                if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='PRIVATE')).exists()):
                    private_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id), Q(visibility='PRIVATE'))
                    for post in private_list:
                        if str(current_user_uuid) in post.visibleTo:
                            private_posts_list.append(post)

                if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend.id), Q(visibility='SERVERONLY')).exists()):
                    if (Helpers.get_current_user_host(request)==friend.host):
                        serveronly_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend.id),Q(visibility='SERVERONLY'))
           
                friends_of_this_friend =  Helpers.get_friends(friend.id)
                for friend_of_this_friend in friends_of_this_friend:
                    if friend_of_this_friend.id != current_user_uuid:
                        if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend_of_this_friend.id), Q(visibility='FOAF')).exists()):
                            foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend_of_this_friend.id),Q(visibility='FOAF'))
            
            if not isRemote:
                remotePosts = pull_remote_nodes(current_user_uuid)

            posts_list = my_posts_list+public_posts_list+friend_posts_list+private_posts_list+serveronly_posts_list+foaf_posts_list+remotePosts
            posts_list.sort(key=lambda x: x.published, reverse=True) # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects answered Dec 31 '08 at 16:42 by Triptych
            paginator = CustomPagination()
            results = paginator.paginate_queryset(posts_list, request)
            serializer=PostSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data) 
        else:
            return Response("User UUID not found", status=404)


# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset answered Oct 14 '13 at 13:11 Aamir Adnan
class PostToUserIDHandler(APIView):
    def get(self, request, user_id, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if type(current_user_uuid) == UUID:
            public_posts_list=[]
            friend_posts_list=[]
            private_posts_list=[]
            serveronly_posts_list=[]
            foaf_posts_list=[]
            if (Post.objects.filter(Q(unlisted=False), Q(author_id=user_id),Q(visibility='PUBLIC')).exists()):
                public_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id),Q(visibility='PUBLIC'))

            isFriend = Helpers.check_two_users_friends(current_user_uuid, user_id)
            if isFriend:
                if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id),Q(visibility='FRIENDS')).exists()):
                    friend_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='FRIENDS'))

                if (Post.objects.filter(Q(unlisted=False), Q(author_id=user_id), Q(visibility='FOAF')).exists()):
                    foaf_posts_list += get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=user_id),Q(visibility='FOAF'))

                if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id), Q(visibility='PRIVATE')).exists()):
                    private_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='PRIVATE'))
                    for post in private_list:
                        if str(current_user_uuid) in post.visibleTo:
                            private_posts_list.append(post)

                if (Post.objects.filter(Q(unlisted=False),Q(author_id=user_id), Q(visibility='SERVERONLY')).exists()):
                    user_host = Author.objects.get(id=user_id)
                    if (Helpers.get_current_user_host(request)==user_host):
                        serveronly_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False),Q(author_id=user_id),Q(visibility='SERVERONLY'))
                
                friends_of_this_friend =  Helpers.get_friends(user_id)
                for friend_of_this_friend in friends_of_this_friend:
                    if (Post.objects.filter(Q(unlisted=False), Q(author_id=friend_of_this_friend.id), Q(visibility='FOAF')).exists()):
                        foaf_posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(unlisted=False), Q(author_id=friend_of_this_friend.id),Q(visibility='FOAF'))

            posts_list = public_posts_list+friend_posts_list+private_posts_list+serveronly_posts_list+foaf_posts_list
            posts_list.sort(key=lambda x: x.published, reverse=True)
            paginator = CustomPagination()
            results = paginator.paginate_queryset(posts_list, request)
            serializer=PostSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)  
        else:
            return current_user_uuid


# For local using only
class MyPostHandler(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
        if type(current_user_uuid) == UUID:
            posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=current_user_uuid))
            paginator = CustomPagination()
            results = paginator.paginate_queryset(posts_list, request)
            serializer=PostSerializer(results, many=True)
            return paginator.get_paginated_response(serializer.data)  
        else:
            return current_user_uuid


def pull_remote_nodes(current_user_uuid):
    remotePosts = []
    for node in Node.objects.all():
        nodeURL = node.host+"service/author/posts/?author_uuid="+str(current_user_uuid)
        response = requests.get(nodeURL, auth=requests.auth.HTTPBasicAuth(node.remoteUsername, node.remotePassword))
        data = json.loads(response.content.decode('utf8').replace("'", '"'))
        if int(data["count"]) != 0: 
            for i in range (0,len(data["posts"])):
                remoteAuthorJson = data["posts"][i]["author"]
                remoteAuthorObj = Helpers.get_or_create_author_if_not_exist(remoteAuthorJson)
                # Create the post object for final list
                if not Post.objects.filter(postid=data["posts"][i]["postid"]).exists():
                    remotePostObj = Post.objects.create(postid=data["posts"][i]["postid"], title=data["posts"][i]["title"],source=data["posts"][i]["source"], 
                        origin=data["posts"][i]["origin"], content=data["posts"][i]["content"],categories=data["posts"][i]["categories"], 
                        contentType=data["posts"][i]["contentType"], author=remoteAuthorObj,visibility=data["posts"][i]["visibility"], 
                        visibleTo=data["posts"][i]["visibleTo"], description=data["posts"][i]["description"],
                        unlisted=data["posts"][i]["unlisted"], published=data["posts"][i]["published"])
                        #https://stackoverflow.com/questions/969285/how-do-i-translate-an-iso-8601-datetime-string-into-a-python-datetime-object community wiki 5 revs, 4 users 81% Wes Winham
                    publishedObj = dateutil.parser.parse(data["posts"][i]["published"])
                    remotePostObj.published = publishedObj
                    remotePostObj.save()
                    remotePosts.append(remotePostObj)

    return remotePosts