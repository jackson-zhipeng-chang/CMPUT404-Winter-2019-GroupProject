from rest_framework import serializers
from .models import Post


# Reference: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('post_id', 'post_title', 'post_content','post_type', 'author', 'open_to')
