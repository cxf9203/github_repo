from django.contrib import admin

# Register your models here.


#day3 注册模型
from .models import abbrobot,WorkingHistory
admin.site.register(abbrobot)
admin.site.register(WorkingHistory)

