from django.shortcuts import render
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404, render
from .models import Post
from .serializers import PostSerializer


# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/45205039/post-to-django-rest-framework

@login_required(login_url="home")
@api_view(['GET','POST', 'PUT', 'DELETE'])
def PostHandler(request, post_id):
    print("uafhofho;d")
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'GET':
    	return Response(PostSerializer(post).data)
    elif request.method == 'POST':
    	return Response({"message": "POST method", "data": post})    
    elif request.method == 'PUT':
        return Response({"message": "PUT method", "data": request.data})
    elif request.method == 'DELETE':
        return Response({"message": "DELETE Method", "data": request.data})


