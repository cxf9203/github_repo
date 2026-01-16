"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

"""
函数 include() 允许引用其它 URLconfs。每当 Django 遇到 include() 时，它会截断与此项匹配的 URL 的部分，并将剩余的字符串发送到 URLconf 以供进一步处理。

我们设计 include() 的理念是使其可以即插即用。因为投票应用有它自己的 URLconf( polls/urls.py )，他们能够被放在 "/polls/" ， "/fun_polls/" ，"/content/polls/"，或者其他任何路径下，这个应用都能够正常工作。"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
urlpatterns = [
    # 添加这一行：将根路径 '/' 永久重定向到 '/myline/index'
    # 修改这里：将根路径 '/' 重定向到 '/myline/index'
    path('', RedirectView.as_view(url='/myline/index', permanent=False), name='index_redirect'),
     #permanent=True: 这会发送 HTTP 301 状态码。如果你只是临时测试，
    # 或者希望浏览器每次都重新请求服务器而不是使用缓存，可以将其改为 False（发送 302 状态码）。
    
    path("myline/", include("myline.urls")),
    
    #path("polls/", include("polls.urls")),# 当包括其它 URL 模式时你应该总是使用 include() ， admin.site.urls 是唯一例外。
    path('admin/', admin.site.urls),
]
