from django.db import models


#day3  添加你的机器人设备对象 模型 （将关联到数据库）
# Create your models here.
class abbrobot(models.Model):
    abbrobot_name = models.CharField(verbose_name="机器人名字", max_length=200)
    abbrobot_number = models.CharField(verbose_name="机器人编号", max_length=200)
    ip_address = models.CharField(verbose_name="IP地址", max_length=200)
    real_product_number = models.BigIntegerField(verbose_name="实时数量", default=0)
    good_product_number = models.BigIntegerField(verbose_name="良品数量", default=0)
    working_state = models.IntegerField(verbose_name="工作状态", choices=[(1, '运行'), (0, '停止'),(2,'故障')], default=0)
    cycle_time = models.FloatField(verbose_name="节拍时间", default=0)
    update_date = models.DateTimeField(verbose_name="更新日期", auto_now=True)
    
    def __str__(self):
        return self.abbrobot_name
    
class WorkingHistory(models.Model):#设备冲压历史

    """
    设备冲压历史记录模型类
    用于记录设备的冲压次数、更新日期和每日增加数量等信息
    """
    device_id = models.ForeignKey(to=abbrobot, to_field="id", on_delete=models.CASCADE, default=1)  # 关联设备ID，外键关联到ABBrobot表的id字段
    number_history = models.BigIntegerField(verbose_name="运行数量", default=0)  # 冲压总次数，使用BigIntegerField存储大整数值，默认值为0
    
    good_number =  models.BigIntegerField(verbose_name="良品数量", default=0)
    update_date = models.DateTimeField(verbose_name= "更新日期",auto_now=True)