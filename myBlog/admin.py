from django.contrib import admin
from .models import Post, Author, Comment,Friend, Node, RemoteUser

# Register your models here.
admin.site.register(Post)
admin.site.register(Author)
admin.site.register(Comment)
admin.site.register(Friend)
admin.site.register(Node)
admin.site.register(RemoteUser)
