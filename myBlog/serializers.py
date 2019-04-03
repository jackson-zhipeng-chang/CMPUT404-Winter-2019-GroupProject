from rest_framework import serializers
from .models import Post, Comment, Author, Friend
import uuid
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response



# Reference: https://www.django-rest-framework.org/api-guide/serializers/#modelserializer
# https://stackoverflow.com/questions/35522768/django-serializer-imagefield-to-get-full-url answered Feb 20 '16 at 11:57 blacklwhite
# https://www.django-rest-framework.org/api-guide/fields/
# https://www.django-rest-framework.org/api-guide/fields/#serializermethodfield
# https://stackoverflow.com/questions/45446953/django-rest-framework-adding-a-custom-field-to-a-paginated-viewset answered Aug 1 '17 at 20:33 Bear Brown
# https://www.django-rest-framework.org/api-guide/pagination/
# https://www.django-rest-framework.org/api-guide/pagination/#pagenumberpagination
# https://www.programcreek.com/python/example/92963/rest_framework.pagination.PageNumberPagination
class CustomPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'size'
    max_page_size = 10000
    def get_paginated_response(self, data):
        if ('posts' in self.request.path and 'comments' not in self.request.path):
            query = 'posts'
        else:
            query = 'comments'

        if self.get_previous_link() is None and self.get_next_link() is None:
            responsBody = {
            'query': query,
            'count': self.page.paginator.count,
            "size": self.page_size,
             query:data,
        }

        elif self.get_next_link() is None:
            responsBody = {
            'query': query,
            'count': self.page.paginator.count,
            "size": self.page_size,
            'previous': self.get_previous_link(),
             query:data,
        }

        elif self.get_previous_link() is None:
            responsBody = {
            'query': query,
            'count': self.page.paginator.count,
            "size": self.page_size,
            'next': self.get_next_link(),
             query:data,
        }

        else: 
            responsBody = {
            'query': query,
            'count': self.page.paginator.count,
            "size": self.page_size,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
             query:data,
        }

        return Response(responsBody)

class AuthorSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = Author
        fields = ('id','displayName', 'url','host', 'github')

    def get_url(self, obj):
        url = obj.host+"service/author/"+str(obj.id)
        return url

    def update(self, instance, validated_data):
        instance.displayName = validated_data.get('displayName', instance.displayName)
        instance.github = validated_data.get('github', instance.github)
        instance.save()
        return instance

class FriendSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    friend = AuthorSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ('id','author','friend', 'status', 'last_modified_time')
        

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
#https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
    author = AuthorSerializer(read_only=True)
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    pagination_class = CustomPagination

    class Meta:
    	model = Post
    	fields = ('title','source','origin','description','contentType','content','author','categories','count','size','next','comments','published','id','visibility','visibleTo','unlisted')

    def get_comments(self, obj):
        comments = Comment.objects.filter(postid=obj.postid).order_by('published')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_count(self, obj):
        comments_count = Comment.objects.filter(postid=obj.postid).order_by('published').count()
        return comments_count

    def get_size(self, obj):
        return 50

    def get_id(self, obj):
        return obj.postid

    def get_next(self, obj):
        try:
            return obj.origin+"/comments"
        except:
            return None
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        author=self.context['author']
        origin=self.context['origin']
        post = Post.objects.create(author=author, origin=origin, source=origin, **validated_data)
        newPost = Post.objects.get(postid=post.postid)
        newPost.origin=post.origin+"service/posts/"+str(post.postid)
        newPost.source=post.source+"service/posts/"+str(post.postid)
        newPost.save()
        return newPost
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.categories = validated_data.get('categories', instance.categories)
        instance.description = validated_data.get('description', instance.description)
        instance.visibleTo = validated_data.get('visibleTo', instance.visibleTo)
        instance.unlisted = validated_data.get('unlisted', instance.unlisted)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.source = validated_data.get('source', instance.source)
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Comment
        fields = '__all__'

    def create(self, validated_data):
        author = self.context['author']
        postid = self.context['postid']
        comment = Comment.objects.create(author=author, postid=postid, **validated_data)
        comment.save()
        return comment

class AuthorProfileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    friends = serializers.SerializerMethodField()
    class Meta:
        model = Author
        fields = ('id','host','displayName', 'url', 'github', 'friends')

    def get_url(self, obj):
        url = obj.host+"service/author/"+str(obj.id)
        return url

    def get_friends(self, obj):
        friends = Author.objects.filter(id=obj.id)
        serializer = AuthorSerializer(friends, many=True)
        return serializer.data
