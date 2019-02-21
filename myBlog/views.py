from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, render
from .models import Post, Author, Comment
from .serializers import PostSerializer, CommentSerializer, AuthorSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

# https://stackoverflow.com/questions/37752440/relative-redirect-using-meta-http-equiv-refresh-with-gh-pages
# https://www.tutorialspoint.com/How-to-automatically-redirect-a-Web-Page-to-another-URL for redirecting

# Code from: Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/2.1/topics/auth/default/
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username=username,password=password, is_active=False)
            userObj = get_object_or_404(User, username=username)
            author = Author.objects.create(name=username,user=userObj)
            author.save()
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def get_current_user_uuid(request):
    current_user = get_object_or_404(User, pk=request.user.id)
    author = get_object_or_404(Author, user=current_user)
    return author.user_uuid

def verify_current_user(post):
    current_user_uuid = get_current_user_uuid(request)
    post = get_object_or_404(Post, pk=post_id)
    post_visibility = post.open_to
    post_author = post.author_id
    if current_user_uuid == post_author:
        return True
    else:
        return False

# https://www.django-rest-framework.org/api-guide/views/
# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
# https://www.geeksforgeeks.org/python-uploading-images-in-django/
class NewPostHandler(APIView):
    def post(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
        author = get_object_or_404(Author, user_uuid=current_user_uuid)
        data = request.data
        serializer = PostSerializer(data=data, context={'author': author})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
class PostHandler(APIView):
    def get(self, request,post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)
        unlisted_post = post.unlisted
        if unlisted_post:
            serializer = PostSerializer(post)
            return JsonResponse(serializer.data)
        else:
            user_verified = verify_current_user(post)
            if post_visibility == 'public' or (post_visibility == 'me' and user_verified):
                serializer = PostSerializer(post)
                return JsonResponse(serializer.data, status=200)
            else:
                return HttpResponse(status=404)
  
    def put(self, request, post_id, format=None):
        data = request.data
        post = get_object_or_404(Post, pk=post_id)
        user_verified = verify_current_user(post)
        if user_verified:
            serializer = PostSerializer(post, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        else:
            return HttpResponse(status=404)

    def delete(self, request, post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)
        user_verified = verify_current_user(post)
        if user_verified:
            post.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


class CommentHandler(APIView):
    def get(self, request, post_id, format=None):
        commment = get_object_or_404(Comment, post_id=post_id)
        serializer = CommentSerializer(commment)
        return JsonResponse(serializer.data)

    def post(self, request, post_id, format=None):
        current_user_uuid = get_current_user_uuid(request)
        post = get_object_or_404(Post, pk=post_id)
        author = get_object_or_404(Author, user_uuid=current_user_uuid)
        data = request.data
        serializer = CommentSerializer(data=data, context={'author': author, 'post_id':post_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)

    def delete(self, request, post_id, format=None):   
        post = get_object_or_404(Post, pk=post_id) 


# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        current_user_uuid = get_current_user_uuid(request)
        posts = Post.objects.filter(Q(author_id=current_user_uuid) | Q(open_to='public')).order_by('-post_time')
        return Response(PostSerializer(posts, many=True).data)


# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset
class PostToUserIDHandler(APIView):
    def get(self, request, user_id, format=None):
    	posts = Post.objects.filter(author_id=user_id)
    	return Response(PostSerializer(posts, many=True).data)


class AuthorProfileHandler(APIView):
    def get(self, request, user_id, format=None):
        author = get_object_or_404(Author, user_uuid=user_id)
        serializer = AuthorSerializer(author)
        return JsonResponse(serializer.data)

    def put(self, request, user_id, format=None):
        data = request.data
        author = get_object_or_404(Author, user_uuid=user_id)
        current_user_uuid = get_current_user_uuid(request)
        if current_user_uuid == author.user_uuid:
            serializer = AuthorSerializer(author, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        else:
            return HttpResponse(status=404)
  
    def delete(self, request, user_id, format=None):
        author = get_object_or_404(Author, pk=user_id)
        user = get_object_or_404(User, pk=author.user.id)
        current_user_uuid = get_current_user_uuid(request)
        if current_user_uuid == author.user_uuid:
            author.delete()
            user.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)




@login_required(login_url="home")
@api_view(['POST'])
def FriendRequestHandler(request):
    if request.method == 'POST':
        return Response({"message": "POST method", "data": post})    

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
 
