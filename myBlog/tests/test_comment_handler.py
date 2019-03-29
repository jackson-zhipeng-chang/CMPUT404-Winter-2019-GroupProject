from django.test import Client, TestCase
from django.urls import reverse
import uuid
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User

class TestCommentHandler(TestCase):
    def setUp(self):
        self.user1 = User.objects.create(username='testuser1')
        self.user1.set_password('test')
        self.user1.save()
        self.client1 = Client()
        self.client1.login(username='testuser1', password='test')
        self.author1 = Author.objects.create(user=self.user1, displayName='author1',
                                             host='http://127.0.0.1:8000',
                                             github='https://github.com/terrence85561')
        self.user2 = User.objects.create(username='testuser2')
        self.user2.set_password('test')
        self.user2.save()
        self.client2 = Client()
        self.client2.login(username='testuser2', password='test')
        self.author2 = Author.objects.create(user=self.user2, displayName='author2',
                                             host='http://127.0.0.1:8000',
                                             github='https://github.com/terrence85561')
        self.new_post_url = reverse('new_post')

    def test_post_comment(self):
        self.client1.post(self.new_post_url, {
            'title': 'POST1',
            'description': 'post for testing',
            'contentType': 'text/plain',
            'category': 'test',
            'visibility': 'PUBLIC',
            'content': 'test',
            'unlisted': False,
            'visibleTo': "",
        }, 'application/json')
        post = Post.objects.get(author=self.author1)
        post_id = post.postid
        post_origin = post.origin
        comment_url = reverse('comment',args=[post_id])
        response=self.client2.post(comment_url,{
            "query":"addComment",
            "post": post_origin,
            "comment":{
                "author":{
                    "id":self.author2.id,
                    "host":self.author2.host,
                    "displayName":self.author2.displayName,
                    "url":self.author2.host+'/'+str(self.author2.id),
                    "github":self.author2.github
                },
                "comment":"comment from author2",
                "contentType":"text/markdown"
            }
        },'application/json')
        self.assertEquals(response.status_code,200)
        success_response = {
            "query":"addComment",
            "success":True,
            "message":"Comment Added"
        }
        self.assertEquals(json.loads(response.content),success_response)
        response = self.client2.post(comment_url, {
            "query":"addCommentWrong",
            "post": post_origin,
            "comment": {
                "author": {
                    "id": self.author2.id,
                    "host": self.author2.host,
                    "displayName": self.author2.displayName,
                    "url": self.author2.host + '/' + str(self.author2.id),
                    "github": self.author2.github
                },
                "comment": "comment from author2",
                "contentType": "text/markdown"
            }
        }, 'application/json')
        self.assertEquals(response.status_code,403)
        # # add comments on a private post
        # self.client1.post(self.new_post_url, {
        #     'title': 'POST2',
        #     'description': 'post for testing',
        #     'contentType': 'text/plain',
        #     'category': 'test',
        #     'visibility': 'PRIVATE',
        #     'content': 'test',
        #     'unlisted': False,
        #     'visibleTo': "",
        # }, 'application/json')
        # post = Post.objects.get(author=self.author1,title='POST2')
        # post_id = post.postid
        # post_origin = post.origin
        # comment_url = reverse('comment', args=[post_id])
        # response = self.client2.post(comment_url, {
        #     "query": "addComment",
        #     "post": post_origin,
        #     "comment": {
        #         "author": {
        #             "id": self.author2.id,
        #             "host": self.author2.host,
        #             "displayName": self.author2.displayName,
        #             "url": self.author2.host + '/' + str(self.author2.id),
        #             "github": self.author2.github
        #         },
        #         "comment": "comment from author2",
        #         "contentType": "text/markdown"
        #     }
        # }, 'application/json')
        # self.assertEquals(response.status_code,403)

