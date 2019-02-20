from rest_framework import serializers
from .models import Post, Comment, Author
import uuid



# Reference: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# https://stackoverflow.com/questions/35522768/django-serializer-imagefield-to-get-full-url
# https://www.geeksforgeeks.org/python-uploading-images-in-django/
# https://www.django-rest-framework.org/api-guide/fields/

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('user_uuid', 'host')

class AuthorFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('name', 'user_uuid','host', 'github')

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.github = validated_data.get('github', instance.github)
        instance.save()
        return instance

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    author = AuthorSerializer()
    class Meta:
    	model = Post
    	fields = ('post_id', 'post_title', 'post_content','post_type', 'author', 'open_to', 'image', 'comments')

    def get_comments(self, obj):
        comments = Comment.objects.filter(post_id=obj.post_id).order_by('comment_time')
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
        instance.post_title = validated_data.get('post_title', instance.post_title)
        instance.post_content = validated_data.get('post_content', instance.post_content)
        instance.post_type = validated_data.get('post_type', instance.post_type)
        instance.open_to = validated_data.get('open_to', instance.open_to)
        instance.save()
        return instance

class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    class Meta:
        model =Comment
        fields = ('comment_id', 'post_id', 'author','content', 'comment_time')

    def create(self, validated_data):
        author = self.context['author']
        post_id = self.context['post_id']
        comment = Comment.objects.create(author=author, post_id=post_id, **validated_data)
        comment.save()
        return comment