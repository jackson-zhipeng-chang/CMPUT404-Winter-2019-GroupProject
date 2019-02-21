from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, render
from .models import Post
from .serializers import PostSerializer
from rest_framework.parsers import JSONParser
from rest_framework import status
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.views import generic
from django.http import HttpResponse, JsonResponse
from django.views.generic.edit import FormView


class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm  # The Form class the FormView should use
    success_url = '/'  # Go here after successful POST

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')

        # is_active should equal true so user can login
        User.objects.create_user(username=username, password=password, is_active=True)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm # The Form class the FormView should use
    success_url = '/'  # Go here after successful POST

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
        else:
            raise Exception  # TODO: better error checking?
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)


def logout_user(request):
    logout(request)
    return redirect("home")


'''
# Code from: Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/2.1/topics/auth/default/
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username=username,password=password, is_active=False)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
'''


# https://www.django-rest-framework.org/api-guide/views/
# https://www.django-rest-framework.org/tutorial/2-requests-and-responses/
# https://www.django-rest-framework.org/tutorial/1-serialization/
class NewPostHandler(APIView):
    def post(self, request, format=None):
        current_user_id = int(self.request.user.id)
        data = JSONParser().parse(request)
        serializer = PostSerializer(data=data, context={'author': current_user_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostHandler(APIView):
    def get(self, request,post_id, format=None):
        current_user_id = int(self.request.user.id)
        post = get_object_or_404(Post, pk=post_id)
        post_visibility = post.open_to
        post_author = int(post.author_id)
        if post_visibility == 'public' or (post_visibility == 'me' and current_user_id == post_author):
            serializer = PostSerializer(post)
            return JsonResponse(serializer.data)
        else:
            return HttpResponse(status=404)
  
    def put(self, request, post_id, format=None):
        data = JSONParser().parse(request)
        post = get_object_or_404(Post, pk=post_id)
        current_user_id = int(self.request.user.id)
        post_author = int(post.author_id)
        if current_user_id == post_author:
            serializer = PostSerializer(post, data=data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data)
            return JsonResponse(serializer.errors, status=400)
        else:
            return HttpResponse(status=404)

    def delete(self, request, post_id, format=None):
        post = get_object_or_404(Post, pk=post_id)
        current_user_id = int(self.request.user.id)
        post_author = int(post.author_id)
        if current_user_id == post_author:
            post.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


@login_required(login_url="home")
@api_view(['GET','POST', 'PUT', 'DELETE'])
def CommentHandler(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'GET':
        return Response(PostSerializer(post).data)
    elif request.method == 'POST':
        return Response({"message": "POST method", "data": post})
    elif request.method == 'PUT':
        return Response({"message": "PUT method", "data": request.data})
    elif request.method == 'DELETE':
        return Response({"message": "DELETE Method", "data": request.data})


@login_required(login_url="home")
@api_view(['POST'])
def FriendRequestHandler(request):
    if request.method == 'POST':
        return Response({"message": "POST method", "data": post})

# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django
# https://www.django-rest-framework.org/api-guide/views/

class PostToUserHandlerView(APIView):

    def get(self, request, format=None):
        current_user_id = int(self.request.user.id)
        posts = Post.objects.filter(author_id=current_user_id)
        return Response(PostSerializer(posts, many=True).data)


# https://stackoverflow.com/questions/19360874/pass-url-argument-to-listview-queryset
class PostToUserIDHandler(APIView):

    def get(self, request, user_id, format=None):
        posts = Post.objects.filter(author_id=user_id)
        return Response(PostSerializer(posts, many=True).data)

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


@login_required(login_url="home")
@api_view(['GET'])
def AuthorProfileHandler(request, user_id):
    if request.method == 'GET':
        return Response({"message": "GET method", "data": post})
