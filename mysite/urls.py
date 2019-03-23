"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Reference: https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
# Reference: http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/swagger.html
# Reference: https://simpleisbetterthancomplex.com/tutorial/2017/02/18/how-to-create-user-sign-up-view.html
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView 
from rest_framework_swagger.views import get_swagger_view
from myBlog import Accounts, Helpers
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('service/', include('myBlog.urls'), name='service'),
    path('', Helpers.home, name='home'),
    path('accounts/login/', Accounts.LoginView.as_view(), name='login'),
    path('accounts/logout/', Accounts.logout_user, name='logout'),
    path('accounts/signup/', Accounts.signup, name='signup'),
    

]