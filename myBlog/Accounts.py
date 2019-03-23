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
from . import Helpers
from django.conf import settings

# https://stackoverflow.com/questions/37752440/relative-redirect-using-meta-http-equiv-refresh-with-gh-pages answered Jun 10 '16 at 19:13 David Jacquel
# https://www.tutorialspoint.com/How-to-automatically-redirect-a-Web-Page-to-another-URL for redirecting
# Code from: Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
# https://docs.djangoproject.com/en/2.1/topics/auth/default/
class LoginView(FormView):
    template_name = 'login.html'
    form_class = AuthenticationForm # The Form class the FormView should use
    success_url = settings.LOGIN_REDIRECT_URL  # Go here after successful POST

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        else:
            return Response("User coudn't find", status=404)
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

# https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url answered Mar 8 '12 at 23:17 kgr, edited Jul 22 '18 at 15:35 wim
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = User.objects.create_user(username=username,password=password, is_active=False)
            userObj = get_object_or_404(User, username=username)
            host = Helpers.get_host_from_request(request)
            author = Author.objects.create(displayName=username,user=userObj, host=host)
            author.save()
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL) 