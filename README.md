# github_repo
# 智能产线综合应用实训

## 项目结构目录

```
github_repo/
├── README.md   #你要读这个说明文档
└── 智能产线综合应用实训/
    ├── ABB_robot_vision/              # ABB机器人视觉处理模块
    │   ├── readCamera/                # 相机读取相关代码
    │   │   ├── MvImport/              # 海康相机SDK封装库
    │   │   │   ├── CamOperation_class.py      # 相机操作类
    │   │   │   ├── CameraParams_const.py      # 相机参数常量
    │   │   │   ├── CameraParams_header.py     # 相机参数头文件
    │   │   │   ├── MvCameraControl_class.py   # 相机控制类
    │   │   │   ├── MvErrorDefine_const.py     # 错误定义常量
    │   │   │   └── PixelType_header.py        # 像素类型头文件
    │   │   ├── cvReadCam.py          # OpenCV读取相机
    │   │   ├── day4_socket_vision_with_hik.py  # 第4天
    │   │   ├── socket_vision_with_hik.py      # 主程序：Socket+海康相机视觉处理（第2天）
    │   │   └── 海康机器人USB3.0工业面阵相机用户手册V2.2.1.pdf
    │   └── sockettest_optimized.py   # Socket测试程序
    ├── line/                         # 产线管理系统
    │   └── myproject/                # Django项目主目录
    │       ├── day4查看数据库中所有的表.py
    │       ├── day4查看该数据表.py
    │       ├── get_db+data.py        # 数据库获取脚本测试用
    │       ├── manage.py             # Django管理脚本
    │       ├── myline/               # Django应用
    │       │   ├── __init__.py
    │       │   ├── admin.py          # 管理后台配置
    │       │   ├── apps.py           # 应用配置
    │       │   ├── migrations/       # 数据库迁移文件
    │       │   │   ├── 0001_initial.py
    │       │   │   ├── 0002_abbrobot_good_product_number.py
    │       │   │   ├── 0003_workinghistory.py
    │       │   │   └── __init__.py
    │       │   ├── models.py         # 数据模型
    │       │   ├── static/           # 静态文件
    │       │   │   └── myline/
    │       │   │       ├── css/
    │       │   │       ├── images/
    │       │   │       ├── img/
    │       │   │       ├── js/
    │       │   │       ├── screen/
    │       │   │       ├── scss/
    │       │   │       ├── style.css
    │       │   │       └── testtttt.html
    │       │   ├── templates/        # 模板文件
    │       │   │   ├── layout.html
    │       │   │   └── myline/
    │       │   │       ├── add_robot.html
    │       │   │       ├── index.html
    │       │   │       ├── robot_list.html
    │       │   │       ├── screen/
    │       │   │       ├── screen.html
    │       │   │       └── workinghistory.html
    │       │   ├── tests.py          # 测试文件
    │       │   ├── urls.py           # URL路由配置
    │       │   └── views.py          # 视图函数
    │       └── myproject/           # Django项目配置
    │           ├── __init__.py
    │           ├── asgi.py            # ASGI配置
    │           ├── settings.py       # 项目设置
    │           ├── urls.py            # 主URL路由
    │           └── wsgi.py            # WSGI配置
    ├── requirements.txt             # 项目依赖包列表
    ├── 启动服务.bat                 # 启动服务脚本
    └── 点我运行安装依赖项.bat       # 安装依赖项脚本
```

## 项目说明

本项目是一个智能产线综合应用实训系统，主要包含以下两个核心模块：

### 1. ABB机器人视觉处理模块 (ABB_robot_vision)
- 使用海康工业相机进行图像采集
- 通过Socket与ABB机器人进行通信
- 实现颜色检测、形状识别等视觉处理功能
- 将检测结果存储到SQLite数据库

### 2. 产线管理系统 (line)
- 基于Django框架开发的Web管理系统
- 管理机器人工作历史记录
- 提供数据可视化展示
- 支持机器人参数配置

## DAY1 使用说明

### 1. 环境准备
- 确保已安装Python 3.8或更高版本
- 安装Django 3.2或更高版本
- 安装其他依赖包，可以使用`requirements.txt`文件进行安装
- ！！！赖人方法，直接双击运行 `点我运行安装依赖项.bat`脚本即可

### 2. 启动服务
- 运行`启动服务.bat`脚本，启动Django开发服务器
- 在浏览器中访问`http://localhost:8000/`查看系统界面
- 可以通过`http://localhost:8000/admin/`访问Django管理后台进行数据管理
### 这时你应该可以看到主页，并且应该可以访问大屏 screen 了

## DAY2 使用说明
### 1.编写ABB实体工业机器人 ，使用socket 机器人与PC 电脑进行通信
- 实现调试好海康工业相机，IP设置、焦距等
- 运行`socket_vision_with_hik.py`脚本，测试Socket通信功能，并与机器人完成简单视觉处理任务实现Socket+海康相机视觉处理功能
- 编写好机器人程序，实现机器人与PC 电脑进行通信


## DAY3 使用说明
### 1.编写Django框架的Web管理系统
- 使用Django框架开发Web管理系统，实现机器人设备、工作历史记录管理
- 实现数据可视化展示，支持机器人参数配置

### 2. 定义好数据库模型
- 在`models.py`文件中定义`abbrobot`和`WorkingHistory`模型，分别用于存储机器人信息和工作历史记录

### 3. 编写URL路由（事先在你需要的html中设定好url）
- 在`urls.py`文件中编写URL路由，将视图函数与URL路径进行映射，实现页面跳转和功能调用
### 4. 编写视图函数
- 在`views.py`文件中编写视图函数，实现机器人设备列表、添加、历史记录查询等功能
- 实现数据可视化展示，支持机器人参数配置

### 5. 编写模板文件
- 在`templates/myline/`目录下编写模板文件，实现页面布局和数据展示

### 6. 启动服务
- 运行`启动服务.bat`脚本，启动Django开发服务器
- 在浏览器中访问`http://localhost:8000/`查看系统界面



## DAY4 使用说明
### 1. 数据库操作
- 使用`day4查看数据库中所有的表.py`脚本查看数据库中所有的表
- 使用`day4查看该数据表.py`脚本查看指定数据表的内容

### 2. 完善day4socket_vision_with_hik.py 程序
- 完善day4socket_vision_with_hik.py 程序，实现机器人与PC 电脑进行通信与视觉处理，
并根据表结构，将视觉处理结果插入历史工作数据库 `myline_workinghistory `

### 3. 启动服务
- 运行`启动服务.bat`脚本，启动Django开发服务器
- 在浏览器中访问`http://localhost:8000/`查看系统界面


## DAY5 总结

### 项目完成情况回顾

经过5天的实训，我们成功完成了一个完整的智能产线综合应用系统，主要成果包括：

#### 技术实现
1. **视觉处理模块**
   - 成功集成海康工业相机，实现图像采集
   - 实现Socket通信，完成机器人与PC的数据交互
   - 开发颜色检测和形状识别算法
   - 实现视觉检测结果自动存储到数据库

2. **Web管理系统**
   - 基于Django框架搭建完整的Web管理系统
   - 实现机器人设备管理功能
   - 开发工作历史记录管理系统
   - 实现数据可视化大屏展示
   - 完成URL路由、视图函数和模板文件的编写

#### 技能提升
1. **编程能力**
   - 掌握Python高级编程技巧
   - 熟练使用OpenCV进行图像处理
   - 掌握Socket网络编程
   - 深入理解Django框架的MVC架构

2. **系统集成**
   - 学会硬件与软件的集成方法
   - 掌握工业相机与计算机的通信
   - 实现多系统间的数据交互

3. **数据库应用**
   - 熟练使用SQLite数据库
   - 掌握Django ORM的使用
   - 实现数据库迁移和版本管理

#### 项目亮点
1. 完整的工业自动化解决方案
2. 模块化设计，易于扩展和维护
3. 友好的用户界面和可视化展示
4. 稳定的数据采集和存储机制

#### 未来可扩展方向
1. 增加更多视觉检测算法（缺陷检测、尺寸测量等）
2. 实现多机器人协同工作
3. 添加数据分析和预测功能
4. 开发移动端应用
5. 集成更多工业设备（PLC、传感器等）



### 答辩注意事项

#### 1. 材料准备
- 准备完整的演示环境，确保所有功能正常运行
- 提前测试海康相机、ABB机器人等硬件设备
- 准备项目演示流程清单，按步骤进行演示
- 准备备用方案，以防演示过程中出现意外

#### 2. 技术准备
- 熟悉项目的整体架构和各模块功能
- 掌握关键技术点的实现原理
- 准备好可能被问到的技术问题的答案
- 了解项目的优缺点和改进空间

#### 3. 演示准备
- 提前规划演示流程，确保在规定时间内完成
- 准备演示脚本，包括操作步骤和讲解要点
- 测试演示环境，确保网络、电源等正常
- 准备演示数据的备份








## 注意事项
- 请确保在使用本项目时遵守相关法律法规和道德规范
- 本项目仅供学习和研究使用，不得用于商业目的

