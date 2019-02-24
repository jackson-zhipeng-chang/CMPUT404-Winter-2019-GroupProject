from django.test import Client, TestCase
from django.urls import reverse
import uuid
import json
from myBlog.models import Author,Post,Comment,Friend
from django.contrib.auth.models import User


class TestViews(TestCase):
    def setUp(self):
        # https://stackoverflow.com/questions/2619102/djangos-self-client-login-does-not-work-in-unit-tests
        self.user = User.objects.create(username='testuser')
        self.user.set_password('test')

        self.user.save()
        self.client = Client()
        self.client.login(username='testuser', password='test')

        self.new_post_url = reverse('new_post')

    # def test_New_Post_Handler_POST_API(self):
    #     author = Author.objects.create(user=self.user,displayName="Test_author",github='https://github.com/terrence85561')
    #
    #     response = self.client.post(self.new_post_url,{
    #         'title': 'POST1',
    #         'description': 'post for testing',
    #         'contentType': 'text/plain',
    #         'visibility': 'PUBLIC',
    #         'content': 'test'
    #     })
    #     self.assertEquals(response.status_code, 200)

    def test_Post_Handler_GET_API(self):
        # test get other author's post
        # create an Author and User for this author
        other_author_user_obj = User.objects.create(username='other_author_user_obj')
        other_author_user_obj.set_password('test')
        other_author_user_obj.save()
        other_author_user_obj_client = Client()
        other_author_user_obj_client.login(username='other_author_user_obj',password='test')
        post_author = Author.objects.create(user=other_author_user_obj,displayName='author',github='https://github.com/terrence85561')

        post1_postid=uuid.uuid4()
        other_author_user_obj_client.post(self.new_post_url,{
                'title': 'original post',
                'postid': post1_postid,
                'content': 'This is a test post',
                'categories': 'test',
                'contentType': 'text/plain',
                'author': post_author,
                'visibility': 'PUBLIC',
                'description': 'test description'

        })
        post1 = Post.objects.create(
            postid=post1_postid,
            title='original post',
            content='This is a test post',
            categories='test',
            contentType='text/plain',
            author=post_author,
            visibility='PUBLIC',
            description='test description'
        )
        modify_post_url = reverse('modify_post',args=[post1_postid])

        response = self.client.get(modify_post_url)

        self.assertEquals(response.status_code,200)
        # test get my post
        # response = None
        # self.assertEquals(response.status_code,200)