
#对pip 进行更新，防止安装依赖项时出现版本问题，更新源使用清华镜像源
#更新pip
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install --upgrade pip

#安装依赖项，源使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

pause