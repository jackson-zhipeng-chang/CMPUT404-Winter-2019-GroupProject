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
    #https://blog.csdn.net/laikaikai/article/details/80563387
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_name = models.CharField(max_length=128,unique=True)
    password = models.CharField(max_length=256)
    friends = models.ManyToManyField('self', blank=True, null=True,related_name='friends')


    def checkfriend(self,username):
        if username in self.friends.all():
            return True
        else:
            return False


    def __str__(self):
        return self.user_name




class Comment(models.Model):     
    post = models.ForeignKey(Post)                      
    author = models.ForeignKey(settings.AUTH_USER_MODEL)                                          
    content = models.TextField()
       
    class Meta:
        db_table = 'comment'
        verbose_name_plural = u'comment'
        
    def __unicode__(self):
        return self.content
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), { 'post_pk': self.post.pk })
