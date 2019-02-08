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
    post_type = models.CharField(max_length=32, choices=postType)
    author_id = models.ForeignKey(User, related_name='author', on_delete=models.PROTECT)

    def __str__(self):
    	return self.post_title
