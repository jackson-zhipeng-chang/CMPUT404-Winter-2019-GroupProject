from django.shortcuts import render
from rest_framework_swagger.views import get_swagger_view
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view


# https://www.django-rest-framework.org/api-guide/views/
# https://stackoverflow.com/questions/45205039/post-to-django-rest-framework

@login_required(login_url="home")
@api_view(['GET', 'POST'])
def Post(request):
    if request.method == 'POST':
        return Response({"message": "Got some data!", "data": request.data})
    return Response({"message": "Hello, world!"})


