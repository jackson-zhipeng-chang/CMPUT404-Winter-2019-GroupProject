from django.db import models
import uuid
from django.contrib.auth.models import User


# When create a new model, run migration as follow:
# python3 manage.py makemigrations
# python3 manage.py migrate

class Post(models.Model):
# https://stackoverflow.com/questions/18676156/how-to-properly-use-the-choices-field-option-in-django
    postType = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
    )
    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post_title = models.CharField(max_length=400)
    post_content = models.TextField()
    post_type = models.CharField(max_length=32, choices=postType)
    author = models.ForeignKey(User, related_name='author', on_delete=models.PROTECT)

    #post_comment = models.CharField(max_length=1000)


    def __str__(self):
    	return self.post_title





class User(models.Model):
    # https://blog.csdn.net/laikaikai/article/details/80563387
    # https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html By Vitor Freitas
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True)
    user_name = models.CharField(max_length=128)

    def __str__(self):
        return self.user_name


class Comment(models.Model):    
    comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    post = models.ForeignKey(Post,on_delete=models.PROTECT, related_name='post_comment')                      
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='comment_author')                                          
    content = models.CharField(max_length=400)
    comment_time = models.DateTimeField(auto_now_add=True, blank=True)
       
    def __str__(self):
        return self.content