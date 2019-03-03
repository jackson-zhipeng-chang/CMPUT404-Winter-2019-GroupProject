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

# https://stackoverflow.com/questions/12615154/how-to-get-the-currently-logged-in-users-user-id-in-django
# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/6567831/how-to-perform-or-condition-in-django-queryset
# https://github.com/belatrix/BackendAllStars/blob/master/employees/views.py
# https://github.com/belatrix/BackendAllStars/blob/master/employees/serializers.py
class PostToUserHandlerView(APIView):
    def get(self, request, format=None):
        current_user_uuid = Helpers.get_current_user_uuid(request)
# https://stackoverflow.com/questions/2658291/get-list-or-404-ordering-in-django
        posts_list = get_list_or_404(Post.objects.order_by('-published'), Q(author_id=current_user_uuid) | Q(visibility='PUBLIC'))
        paginator = CustomPagination()
        results = paginator.paginate_queryset(posts_list, request)
        serializer=PostSerializer(results, many=True)
        return paginator.get_paginated_response(serializer.data)   
 