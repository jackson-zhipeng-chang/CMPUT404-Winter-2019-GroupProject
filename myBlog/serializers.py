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
    count = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()
    class Meta:
    	model = Post
    	fields = ('title','source','origin','description','contentType','content','author','categories','count','size','next','comments','published','postid','visibility','visibleTo','unlisted')

    def get_comments(self, obj):
        comments = Comment.objects.filter(postid=obj.postid).order_by('published')
        serializer = CommentSerializer(comments, many=True)
        return serializer.data

    def get_count(self, obj):
        comments_count = Comment.objects.filter(postid=obj.postid).order_by('published').count()
        return comments_count

    def get_size(self, obj):
        return 50

    def get_next(self, obj):
        try:
            return obj.origin+str(obj.postid)+"/comments"
        except:
            return None
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def create(self, validated_data):
        author = self.context['author']
        origin=self.context['origin']
        post = Post.objects.create(author=author, origin=origin, source=origin, **validated_data)
        newPost = Post.objects.get(postid=post.postid)
        newPost.origin=post.origin+str(post.postid)
        newPost.source=post.source+str(post.postid)
        newPost.save()
        return newPost
# https://www.django-rest-framework.org/api-guide/serializers/#saving-instances
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.contentType = validated_data.get('contentType', instance.contentType)
        instance.visibility = validated_data.get('visibility', instance.visibility)
        instance.origin = validated_data.get('origin', instance.origin)
        instance.source = validated_data.get('source', instance.source)
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

class PostResponsSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=10)
    count = serializers.IntegerField()
    size = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    posts = PostSerializer(many=True)

class PostResponsSerializerNoPrevious(serializers.Serializer):
    query = serializers.CharField(max_length=10)
    count = serializers.IntegerField()
    size = serializers.IntegerField()
    next = serializers.URLField()
    posts = PostSerializer(many=True)

class PostResponsSerializerNoNext(serializers.Serializer):
    query = serializers.CharField(max_length=10)
    count = serializers.IntegerField()
    size = serializers.IntegerField()
    previous = serializers.URLField()
    posts = PostSerializer(many=True)
