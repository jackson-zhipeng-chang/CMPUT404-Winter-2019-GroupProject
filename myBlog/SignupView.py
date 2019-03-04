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