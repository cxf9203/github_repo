#__author:StevenChen
#__Date:2021/4/22
import numpy as np
import socket  # 导入 socket 模块
import cv2  #确保已经安装opencv，若没有，请使用pip install opencv-python 若安装速度慢，可以切换镜像源。还是慢断网等问题，可以打开手机热点。
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')人脸识别的xml文件
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
"""这个函数用于检测输入图像中是否存在红色像素点。它使用OpenCV库和NumPy库来实现颜色检测功能。"""
def isRedcolor(img):
    # 检查图片是否成功加载
    if img is None:
        print("错误：无法加载图片，请检查文件路径是否正确。")
    else:
        print("get img")
        # 2. 将图片从 BGR 转换到 HSV 颜色空间
        # OpenCV 默认读取为 BGR，而 HSV 更适合颜色过滤
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # 3. 定义红色的范围
        # 红色在 HSV 色环中首尾相接，所以需要定义两个范围
        # 范围1：较低的红 (H: 0-10)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        
        # 范围2：较高的红 (H: 170-180)
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])

        # 4. 根据范围创建掩膜 (Mask)
        # cv2.inRange 会将介于 lower 和 upper 之间的像素设为白色(255)，其他设为黑色(0)
        mask1 = cv2.inRange(hsv_img, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_img, lower_red2, upper_red2)

        # 5. 合并两个掩膜
        mask = mask1 + mask2

        # 6. 检查是否存在白色像素点（即代表红色像素点）
        # np.any() 函数检查数组中是否至少有一个非零元素
        has_red = np.any(mask)

        if has_red:
            print("图中检测到了红色像素点！")
            
            # 可选：为了直观看到效果，可以将掩膜显示出来
            # cv2.imshow('Red Mask', mask)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            return True
        else:
            print("图中未检测到红色像素点。")
            return False
###请在这里进行图像处理的相关程序，并返回一个bool的结果###
def isImg_ok(my_img):
    #以下为简单的图像处理与结果判断，请按照任务要求描写
    my_img = cv2.cvtColor(my_img, cv2.COLOR_BGR2GRAY)   #彩色空间转gray灰度
    size = my_img.shape #获取图片大小
    if size[0]<3:
        result = True
    else:
        result = False
    return result


###setting###
str_msg = 'hello ABBrobotware    '  # 修改变量名，避免与内置函数str冲突
str_ok = 'ok'
str_NG = 'NG'
str_msg = str_msg.encode() #encode 解码发送
str_ok = str_ok.encode()
str_NG = str_NG.encode()
result = False

# 创建socket对象并设置选项
s = socket.socket()  # 创建 socket 对象，s
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许地址重用
host = socket.gethostname()  # 获取本地主机名     #实体机器人和虚拟机器人ip不一样要注意下
#host = "192.168.100.1"
port = 8005  # 设置端口
print(host)
s.bind((host, port))        # 绑定端口
print(s)
s.listen(30)  # 开始监听，移到循环外

#cap = cv2.VideoCapture(0)此为摄像机读取，取消注释完成摄像机开启

print("等待客户端连接...")
while True:
    try:
        conn, addr = s.accept()     # 建立客户端连接
        print(f"客户端已连接: {addr}")

        while True:
            try:
                data = conn.recv(8005)  # 接收数据
                if not data:  # 如果没有接收到数据，说明客户端已断开连接
                    print("客户端主动断开连接")
                    break

                data = data.decode() #对接受的数据解码
                print('接收到:', data)# 打印接收到的解码数据

                if data == "ready":
                    txt = input("请输入信息，格式为 44.2,23.9,0.0\0D")
                    txt = txt.encode()
                    conn.send(txt)  # 发送消息给ABB工业机器人客户端
                #todo 学生作业请在下面生成图像处理代码，作业时请删除 pass
                elif data == "pic":
                    pass
                    #todo  读取一张图片
                    #frame = cap.read()  # 读取一帧图像
                    img = cv2.imread('appletree.jpg')
                    #todo 识别图中是否右红色像素点
                    result = isRedcolor(img)
                    #todo  根据识别结果发送不同的消息给ABB工业机器人客户端
                    if result == True:  #回调函数返回的result值
                        res = "red"
                        res = res.encode()
                        conn.send(res)  # 发送消息给ABB工业机器人客户端
                       
                    else:
                        res = "not"
                        res = res.encode()
                        conn.send(res)  # 发送消息给ABB工业机器人客户端   
                else:
                    conn.send(str_msg)

                #isImg_ok(frame)   #调用函数，处理frame图片
                #if result == True:  #回调函数返回的result值
                #    conn.send(str_ok)  #PC端发送结果给ABB工业机器人
               # else:
                #    conn.send(str_NG)  #PC端发送结果给ABB工业机器人

            except ConnectionResetError:
                print('客户端连接被重置')
                break
            except BrokenPipeError:
                print('管道破裂，连接已断开')
                break
            except Exception as e:
                print(f'发生未知错误: {str(e)}')
                break

    except Exception as e:
        print(f'服务器错误: {str(e)}')
        break
    finally:
        try:
            conn.close()  # 确保关闭连接
            print("连接已关闭")
        except:
            pass

# 程序结束时关闭socket
try:
    s.close()
except:
    pass

#cv2.destroyAllWindows()
