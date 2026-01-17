from django.shortcuts import render
import os
# Create your views here.
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
#day3 插入数据库模型
from .models import abbrobot,WorkingHistory
from django.utils import timezone
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta
from django.conf import settings
from django import forms
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

#day3 添加表单 step2.1
class AbbModelForm(forms.ModelForm):
    class Meta:
        model = abbrobot #表单模型对象
        fields = ["abbrobot_name","abbrobot_number","ip_address","real_product_number",
                  "good_product_number","working_state","cycle_time"]

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for name,field in self.fields.items():
            field.widget.attrs = {"class":"form-control","placeholder":field.label}




#我的首页视图
def index(request):
    return render(request,'myline/index.html')



#day3 添加robot_list 页面 step1
def robot_list(requests):
    # 从数据库获取数据
    queryset = abbrobot.objects.all().order_by('-working_state','id')
    working_satate = {0:"停止",1:"运行",2:"故障"}
    return render(requests,'myline/robot_list.html',{"queryset": queryset})#去templates/myline文件夹下找robot_list.html


#day3 add_robot 页面 step2
def add_robot(requests):
    form = AbbModelForm() #step2.1
    if requests.method == "GET":
        return render(requests, 'myline/add_robot.html', {"form": form})##step2.2 新增add_robot.html文件
    form = AbbModelForm(data=requests.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('robotlist'))
    else:
        print(form.errors)
        return render(requests, 'myline/add_robot.html', {"form": form})
    
#day3 edit_robot 页面 step3
def screen(requests):
    
    
    
    return render(requests,'myline/screen.html')


#day3 screen 柱状图定期更新 echarts 与 ajax结合 step4
def chart_bar(requests):
    # 从数据库获取数据
    abbqueryset = abbrobot.objects.all().order_by('-real_product_number')[:10]

    namelist = list()
    data = list()
    for obj in abbqueryset:
        namelist.append(obj.abbrobot_name)
        data.append(obj.real_product_number)
    
    xAxis = {
        "axisLabel": {
            "show": True  # 隐藏 y 轴上的标签
        },
        "type": 'category',
        "data": namelist,
        "inverse": False,
        "animationDuration": 300,
        "animationDurationUpdate": 300,
        "max": 8  # only the largest 3 bars will be displayed

    }
    series = [{
        "realtimeSort": True,
        "name": '实时运行数',
        "type": 'bar',
        "data": data,
        "label": {
            "show": True,
            "position": 'right',
            "valueAnimation": True
        },
        'itemStyle': {

            'color': "rgba(25, 255, 255, 1)",

        }
    }
    ]
    ret = {
        "status": True,
        "data": {
            "xAxis": xAxis,
            "series": series,

        }
    }
    # # json_str = json.dumps(data_list)
    # # return HttpResponse(json_str)
    return JsonResponse(ret)

def workinghistory(requests):
    queryset = WorkingHistory.objects.all().order_by('-id')  # 获取倒序的所有数据
   # 设置每页显示的数量
    page_size = 10  # 每页10条数据
    paginator = Paginator(queryset, page_size)

    # 获取当前页码
    page_number = requests.GET.get('page')

    try:
        # 获取当前页的数据
        page_objects = paginator.page(page_number)
    except PageNotAnInteger:
        # 如果page不是一个整数，显示第一页
        page_objects = paginator.page(1)
    except EmptyPage:
        # 如果page超出了范围，显示最后一页
        page_objects = paginator.page(paginator.num_pages)

    return render(requests, 'myline/workinghistory.html', {"page_objects": page_objects})
