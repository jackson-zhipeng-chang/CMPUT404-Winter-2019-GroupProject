from rest_framework import serializers
from .models import Post, Comment, Author
import uuid



# Reference: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# https://stackoverflow.com/questions/35522768/django-serializer-imagefield-to-get-full-url
# https://www.geeksforgeeks.org/python-uploading-images-in-django/
# https://www.django-rest-framework.org/api-guide/fields/
# https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield


class AuthorSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ('id','displayName', 'url','host', 'github')

    def get_url(self, obj):
        url = obj.host+"/"+str(obj.id)
        return url

    def update(self, instance, validated_data):
        instance.displayName = validated_data.get('displayName', instance.displayName)
        instance.github = validated_data.get('github', instance.github)
        instance.save()
        return instance

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
#https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
    author = AuthorSerializer(read_only=True)
    class Meta:
    	model = Post
    	fields = '__all__'

    def get_comments(self, obj):
        comments = Comment.objects.filter(postid=obj.postid).order_by('published')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        author = self.context['author']
        post = Post.objects.create(author=author, **validated_data)
        post.save()
        return post
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model =Comment
        fields = '__all__'

    def create(self, validated_data):
        author = self.context['author']
        postid = self.context['postid']
        comment = Comment.objects.create(author=author, postid=postid, **validated_data)
        comment.save()
        return comment


class ResponsSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=10)
    content = serializers.CharField(max_length=10)
    size = serializers.CharField(max_length=10)
    next = serializers.URLField()
    previous = serializers.URLField()
    posts = PostSerializer(many=True)

