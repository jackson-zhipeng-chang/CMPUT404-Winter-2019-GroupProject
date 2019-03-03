"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Reference: https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
# Reference: http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/swagger.html

from django.contrib import admin
from django.urls import path, include
from . import Helpers, NewPostHandler,PostHandler, CommentHandler, FriendRequestHandler, FriendQueryHandler, PostToUserHandlerView, PostToUserIDHandler, AuthorProfileHandler, Friend2FriendHandler,SignupView, LoginView 
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView 


urlpatterns = [
    path('api-docs/',login_required(get_swagger_view(title='Welcome to myBlog APIs Documentation!')), name='apiDocs'),
    path('posts/', NewPostHandler.NewPostHandler.as_view(), name='new_post'),
    path('posts/<uuid:postid>/', PostHandler.PostHandler.as_view(), name='modify_post'),
    path('posts/<uuid:postid>/comments/', CommentHandler.CommentHandler.as_view(), name='comment'),
    path('friendrequest/', FriendRequestHandler.FriendRequestHandler.as_view(), name='friendrequest'),
    path('friends/<uuid:user_id>/', FriendQueryHandler.FriendQueryHandler.as_view(), name='friendquery'),
    path('author/posts/', login_required(PostToUserHandlerView.PostToUserHandlerView.as_view()), name='posttouser'),
    path('author/<uuid:user_id>/posts/', PostToUserIDHandler.PostToUserIDHandler.as_view(), name='posttouserid'),
    path('author/<uuid:user_id>/', AuthorProfileHandler.AuthorProfileHandler.as_view(), name='authorprofile'),
    path('author/<uuid:user_id1>/friends/<uuid:user_id2>/', Friend2FriendHandler.Friend2FriendHandler, name='friend2friend'),
    path('login/', LoginView.LoginView.as_view(), name='login'),
    path('logout/', Helpers.logout_user, name='logout'),
    path('signup/', SignupView.SignupView.as_view(), name='signup'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
