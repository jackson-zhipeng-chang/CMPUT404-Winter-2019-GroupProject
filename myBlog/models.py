from django.db import models
import uuid
from django.contrib.auth.models import User


# When create a new model, run migration as follow:
# python3 manage.py makemigrations
# python3 manage.py migrate

class Author(models.Model):
    # https://blog.csdn.net/laikaikai/article/details/80563387
    # https://docs.djangoproject.com/en/2.1/topics/db/examples/one_to_one/
    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html By Vitor Freitas
    user_uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    name = models.CharField(max_length=128)
    host = models.URLField(null=True, blank=True)
    github = models.URLField(null=True, blank=False)

    def __str__(self):
        return self.name


class Post(models.Model):
# https://stackoverflow.com/questions/18676156/how-to-properly-use-the-choices-field-option-in-django
    postType = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
    )
    open_toType =(
        ('me', 'me'),
        ('author', 'author'),
        ('friends', 'friends'),
        ('FoF', 'FoF'),
        ('public', 'public'),
    )
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_title = models.CharField(max_length=400)
    post_content = models.TextField()
    post_type = models.CharField(max_length=32, choices=postType)
    author = models.ForeignKey(Author, related_name='post_author', on_delete=models.PROTECT)
    open_to = models.CharField(max_length=32, choices=open_toType)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    def __str__(self):
    	return self.post_title


class Comment(models.Model):    
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    post_id = models.UUIDField(default=uuid.uuid4, editable=False)               
    author = models.ForeignKey(Author,  related_name='comment_author', on_delete=models.PROTECT)                                          
    content = models.CharField(max_length=400)
    comment_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.content