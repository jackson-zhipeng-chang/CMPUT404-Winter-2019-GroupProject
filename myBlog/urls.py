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
from . import views
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView 


urlpatterns = [
    path('api-docs/',login_required(get_swagger_view(title='Welcome to myBlog APIs Documentation!')), name='apiDocs'),
    path('posts/', views.NewPostHandler.as_view(), name='new_post'),
    path('posts/<uuid:postid>/', views.PostHandler.as_view(), name='modify_post'),
    path('posts/<uuid:postid>/comments/', views.CommentHandler.as_view(), name='comment'),
    path('friendrequest/', views.FriendRequestHandler.as_view(), name='friendrequest'),
    path('friends/<uuid:user_id>/', views.FriendQueryHandler.as_view(), name='friendquery'),
    path('author/posts/', login_required(views.PostToUserHandlerView.as_view()), name='posttouser'),
    path('author/<uuid:user_id>/posts/', views.PostToUserIDHandler.as_view(), name='posttouserid'),
    path('author/<uuid:user_id>/', views.AuthorProfileHandler.as_view(), name='authorprofile'),
    path('author/<uuid:user_id1>/friends/<uuid:user_id2>/', views.Friend2FriendHandler, name='friend2friend'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
