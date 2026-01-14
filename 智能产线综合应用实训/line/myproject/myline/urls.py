from django.urls import path

from . import views

urlpatterns = [
    #首页
    path('index/', views.index, name="index"),
    #MES大屏
    path('screen/', views.screen, name="screen"),
]