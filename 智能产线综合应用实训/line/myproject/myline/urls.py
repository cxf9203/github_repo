from django.urls import path

from . import views

urlpatterns = [
    #首页
    path('index/', views.index, name="index"),
    #MES大屏
    path('screen/', views.screen, name="screen"),
    
    #day3 新增 机器人设备列表页面  step1
    path('robot_list/', views.robot_list, name="robotlist"),
    #day3 新增 机器人设备添加页面  step2
    path('add_robot/', views.add_robot, name="add_robot"),
    #day3 新增 大屏柱状图与定时更新ajax  step4
    path('chart_bar/', views.chart_bar,name="chart_bar"),
    #day3 新增 历史记录页面  step5
    path('workinghistory/', views.workinghistory, name="workinghistory"),
]