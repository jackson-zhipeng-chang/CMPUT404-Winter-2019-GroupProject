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
from . import Helpers,PostHandler, CommentHandler, FriendRequestHandler, FriendQueryHandler, AuthorProfileHandler, Friend2FriendHandler,Accounts
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView



urlpatterns = [
    path('api-docs/',login_required(get_swagger_view(title='Welcome to myBlog APIs Documentation!')), name='apiDocs'),
    path('posts/', PostHandler.NewPostHandler.as_view(), name='new_post'),
    path('posts/<uuid:postid>/', PostHandler.PostHandler.as_view(), name='modify_post'),
    path('posts/<uuid:postid>/comments/', CommentHandler.CommentHandler.as_view(), name='comment'),
    path('friendrequest/', FriendRequestHandler.FriendRequestHandler.as_view(), name='friendrequest'),
    path('author/<uuid:user_id>/friends/', FriendQueryHandler.FriendQueryHandler.as_view(), name='friendquery'),
    path('author/posts/',PostHandler.PostToUserHandlerView.as_view(), name='posttouser'),
    path('author/<uuid:user_id>/posts/', PostHandler.PostToUserIDHandler.as_view(), name='posttouserid'),
    path('author/<uuid:user_id>/', AuthorProfileHandler.AuthorProfileHandler.as_view(), name='authorprofile'),
    path('modify_post/<uuid:post_id>/',Helpers.modify_post,name='modify_post'),
    path('author/<str:authorid1>/friends/<str:service2>/author/<str:authorid2>', Friend2FriendHandler.Friend2FriendHandler.as_view(), name='friend2friend'),

    path('', Helpers.home, name='home'),
    path('login/', Accounts.LoginView.as_view(), name='login'),
    path('logout/', Accounts.logout_user, name='logout'),
    path('signup/', Accounts.signup, name='signup'),
    path('all/', Helpers.home, name='postslist'),
    path('newpost/', Helpers.new_post, name='newpost'),
    path('myprofile/', AuthorProfileHandler.MyProfileHandler.as_view(), name='myprofile'),
    path('myprofilepage/', Helpers.my_profile, name='myprofliepage'),
    path('posts/mine/',  PostHandler.MyPostHandler.as_view(), name='myposts_view'),
    path('myposts/', Helpers.my_posts, name='myposts'),
    path('myfriends/', FriendRequestHandler.MyFriends.as_view(), name='myfriends'),
    path('myfriendslist/', Helpers.my_friends, name='myfriendslist'),
    path('frlist/',Helpers.friend_request,name='requestlist'),
    path('authordetails/<author_id>/',Helpers.author_details,name='authordetails'),
    path('postdetails/<post_id>/', Helpers.post_details, name='postdetails'),
    path('unfriend/<friendid>/',FriendRequestHandler.UnFriend.as_view(),name='unfriend'),
    
]
