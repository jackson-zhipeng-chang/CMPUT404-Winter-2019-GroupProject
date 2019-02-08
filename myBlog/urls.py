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


urlpatterns = [
    path('api-docs/', get_swagger_view(title='CMPUT 404 Team 4 API docs'), name='apiDocs'),
    path('posts/<uuid:post_id>/', views.PostHandler, name='post'),
    path('comments/<uuid:post_id>/', views.CommentHandler, name='comment'),
    path('friendrequest/', views.FriendRequestHandler, name='friendrequest'),
    path('friends/<int:user_id>', views.FriendQueryHandler, name='friendquery'),
    path('author/posts/', views.PostToUserHandlerView.as_view(), name='posttouser'),
    path('author/<int:user_id>/posts', views.PostToUserIDHandler.as_view(), name='posttouserid'),
    path('author/<int: userid>', views.AuthorProfileHandler, name='authorprofile'),
    path('author/<int:user_id1>/friends/<int:user_id2>', views.Friend2FriendHandler, name='friend2friend'),
]
