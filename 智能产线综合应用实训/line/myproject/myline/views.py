from django.shortcuts import render
import os
# Create your views here.
from django.http import HttpResponse,JsonResponse,HttpResponseRedirect,Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse
#插入数据库模型
#from .models import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta
from django.conf import settings
from django import forms
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


#我的首页视图
def index(request):
    return render(request,'myline/index.html')

def screen(requests):
    
    
    
    return render(requests,'myline/screen.html')
