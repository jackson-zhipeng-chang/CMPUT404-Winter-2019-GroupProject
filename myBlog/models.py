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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, editable=False)
    displayName = models.CharField(max_length=128)
    github = models.URLField(null=True, blank=False)
    host = models.URLField()

    def __str__(self):
        return self.displayName


class Friend(models.Model):
#https://briancaffey.github.io/2017/07/19/different-ways-to-build-friend-models-in-django.html
# https://stackoverflow.com/questions/2201598/how-to-define-two-fields-unique-as-couple
    friednStatusChoise = (
        ('Accept', 'Accept'),
        ('Decline', 'Decline'),
        ('Pending', 'Pending'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(Author, related_name='sender',on_delete=models.PROTECT, editable=False)
    friend = models.ForeignKey(Author,  related_name='reciver',on_delete=models.PROTECT, editable=False)
    status = models.CharField(max_length=32, choices=friednStatusChoise, default='Pending')
    last_modified_time = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = ('author', 'friend',)


    def __str__(self):
        return "Friend request from %s to %s"%(self.author, self.friend)



class Post(models.Model):
# https://stackoverflow.com/questions/18676156/how-to-properly-use-the-choices-field-option-in-django
    contentTypeChoice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base64'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )
    visibilityType =(
        ('PUBLIC', 'PUBLIC'),
        ('FOAF', 'FOAF'),
        ('FRIENDS', 'FRIENDS'),
        ('PRIVATE', 'PRIVATE'),
        ('SERVERONLY', 'SERVERONLY'),
    )
#https://stackoverflow.com/questions/1110153/what-is-the-most-efficient-way-to-store-a-list-in-the-django-models
    postid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=400)
    source = models.URLField(null=True, blank=True)
    origin = models.URLField(null=True, blank=True)
    content = models.TextField()
    categories = models.TextField(null=True, blank=True)
    contentType = models.CharField(max_length=32, choices=contentTypeChoice)
    author = models.ForeignKey(Author, related_name='post_author', on_delete=models.PROTECT)
    visibility = models.CharField(max_length=32, choices=visibilityType)
    visibleTo = models.TextField(null=True, blank=True)
    description = models.TextField()
#https://stackoverflow.com/questions/5190313/django-booleanfield-how-to-set-the-default-value-to-true
    unlisted = models.BooleanField(default=False)
    published = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
    	return self.title


class Comment(models.Model): 
    contentTypeChoice = (
        ('text/markdown', 'text/markdown'),
        ('text/plain', 'text/plain'),
        ('application/base64', 'application/base64'),
        ('image/png;base64', 'image/png;base64'),
        ('image/jpeg;base64', 'image/jpeg;base64'),
    )   
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) 
    postid = models.UUIDField(default=uuid.uuid4)               
    author = models.ForeignKey(Author,  related_name='comment_author', on_delete=models.PROTECT)                                          
    comment = models.CharField(max_length=400)
    contentType = models.CharField(max_length=32, choices=contentTypeChoice)
    published = models.DateTimeField(auto_now_add=True, blank=True)
    def __str__(self):
        return self.comment

