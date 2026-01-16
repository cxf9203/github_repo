#启动django 服务 路径在line/myproject/manage.py

cd line\myproject
python manage.py runserver 


#开放所有人可以访问服务器
#python manage.py runserver 0.0.0.0：8000
#须本地防火墙开放
#并且在settings.py 中找到并设置 ALLOWED_HOSTS = ['*']


