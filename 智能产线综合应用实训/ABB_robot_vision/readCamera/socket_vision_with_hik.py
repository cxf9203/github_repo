# -- coding: utf-8 --
#__author:StevenChen
#__Date:2026/01/16
import os
import sqlite3
import numpy as np
import socket  # 导入 socket 模块
import cv2  #确保已经安装opencv，若没有，请使用pip install opencv-python 若安装速度慢，可以切换镜像源。还是慢断网等问题，可以打开手机热点。
#face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')人脸识别的xml文件
#eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
#导入海康相机封装后的库
from MvImport.CamOperation_class import *
from MvImport.MvCameraControl_class import *
from MvImport.MvErrorDefine_const import *
from MvImport.CameraParams_header import *

import cv2
import numpy as np
import threading
#创建全局图像变量img
img = None
# 获取选取设备信息的索引，通过[]之间的字符去解析
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()


# 将返回的错误码转换为十六进制显示
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2 ** 32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr
    return hexStr

Stand_color = "RED" #判断标准RED
Stand_shape = "CIRCLE" #判断标准圆形

global deviceList
deviceList = MV_CC_DEVICE_INFO_LIST()
global cam
cam = MvCamera()
global nSelCamIndex
nSelCamIndex = 0
global obj_cam_operation
obj_cam_operation = 0
global isOpen
isOpen = False
global isGrabbing
isGrabbing = False



# ch:枚举相机 | en:enum devices
def enum_devices():
    global deviceList
    global obj_cam_operation

    deviceList = MV_CC_DEVICE_INFO_LIST()
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    if ret != 0:
        strError = "Enum devices fail! ret = :" + ToHexStr(ret)
        #QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
        return ret

    if deviceList.nDeviceNum == 0:
        #QMessageBox.warning(mainWindow, "Info", "Find no device", QMessageBox.Ok)
        return ret
    print("Find %d devices!" % deviceList.nDeviceNum)

    devList = []
    for i in range(0, deviceList.nDeviceNum):
        mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
        if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
            print("\ngige device: [%d]" % i)
            chUserDefinedName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName:
                if 0 == per:
                    break
                chUserDefinedName = chUserDefinedName + chr(per)
            print("device user define name: %s" % chUserDefinedName)

            chModelName = ""
            for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
                if 0 == per:
                    break
                chModelName = chModelName + chr(per)

            print("device model name: %s" % chModelName)

            nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
            nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
            nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
            nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
            print("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
            devList.append(
                "[" + str(i) + "]GigE: " + chUserDefinedName + " " + chModelName + "(" + str(nip1) + "." + str(
                    nip2) + "." + str(nip3) + "." + str(nip4) + ")")
        elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
            print("\nu3v device: [%d]" % i)
            chUserDefinedName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName:
                if per == 0:
                    break
                chUserDefinedName = chUserDefinedName + chr(per)
            print("device user define name: %s" % chUserDefinedName)

            chModelName = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
                if 0 == per:
                    break
                chModelName = chModelName + chr(per)
            print("device model name: %s" % chModelName)

            strSerialNumber = ""
            for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                if per == 0:
                    break
                strSerialNumber = strSerialNumber + chr(per)
            print("user serial number: %s" % strSerialNumber)
            devList.append("[" + str(i) + "]USB: " + chUserDefinedName + " " + chModelName
                            + "(" + str(strSerialNumber) + ")")

# ch:打开相机 | en:open device
def open_device():
    global deviceList
    global nSelCamIndex
    global obj_cam_operation
    global isOpen
    if isOpen:
        return MV_E_CALLORDER

    nSelCamIndex = 0        #相机编号
    if nSelCamIndex < 0:
        return MV_E_CALLORDER
    nSelCamIndex =0
    obj_cam_operation = CameraOperation(cam, deviceList, nSelCamIndex)

    ret = obj_cam_operation.Open_device()
    if 0 != ret:
        strError = "Open device failed ret:" + ToHexStr(ret)
        isOpen = False

# ch:开始取流 | en:Start grab image
def start_grabbing():
    global obj_cam_operation
    
    if not obj_cam_operation.b_start_grabbing and obj_cam_operation.b_open_device:
        obj_cam_operation.b_exit = False
        ret = obj_cam_operation.obj_cam.MV_CC_StartGrabbing()
        if ret != 0:
            print(ret)
        obj_cam_operation.b_start_grabbing = True
        print("start grabbing successfully!")

# ch:停止取流 | en:Stop grab image
def stop_grabbing():
    global obj_cam_operation
    global isGrabbing
    ret = obj_cam_operation.Stop_grabbing()
    if ret != 0:
        strError = "Stop grabbing failed ret:" + ToHexStr(ret)
        #QMessageBox.warning(mainWindow, "Error", strError, QMessageBox.Ok)
    else:
        isGrabbing = False


# ch:关闭设备 | Close device
def close_device():
    global isOpen
    global isGrabbing
    global obj_cam_operation

    if isOpen:
        obj_cam_operation.Close_device()
        isOpen = False

    isGrabbing = False

def work_thread():   
    global img 
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    numArray = None
    stPayloadSize = MVCC_INTVALUE_EX()

    while True:
        ret_temp = obj_cam_operation.obj_cam.MV_CC_GetIntValueEx("PayloadSize", stPayloadSize)
        if ret_temp != MV_OK:
            print("error")
        NeedBufSize = int(stPayloadSize.nCurValue)
        if obj_cam_operation.buf_grab_image_size < NeedBufSize:
            obj_cam_operation.buf_grab_image = (c_ubyte * NeedBufSize)()
            obj_cam_operation.buf_grab_image_size = NeedBufSize

        ret = obj_cam_operation.obj_cam.MV_CC_GetOneFrameTimeout(obj_cam_operation.buf_grab_image, obj_cam_operation.buf_grab_image_size, stFrameInfo)
        
        #ch: 改变像素格式 | en: convert pixel format 
        if stFrameInfo.enPixelType != PixelType_Gvsp_BGR8_Packed:
            pstCvtParam = MV_CC_PIXEL_CONVERT_PARAM()
            pstCvtParam.nWidth = stFrameInfo.nWidth                         #图像宽
            pstCvtParam.nHeight = stFrameInfo.nHeight                       #图像高
            pstCvtParam.pSrcData = obj_cam_operation.buf_grab_image         #输入数据缓存
            pstCvtParam.nSrcDataLen = stFrameInfo.nFrameLen;                #输入数据长度
            pstCvtParam.enSrcPixelType = stFrameInfo.enPixelType            #源像素格式
            pstCvtParam.enDstPixelType = PixelType_Gvsp_BGR8_Packed         #目标像素格式
            nConvertDataSize = stFrameInfo.nWidth * stFrameInfo.nHeight * 3
            pstCvtParam.nDstBufferSize = nConvertDataSize                   #提供的输出缓冲区大小
            buf_save_image = (c_ubyte * nConvertDataSize)()
            pstCvtParam.pDstBuffer = buf_save_image                         #输出数据缓存
            ret = obj_cam_operation.obj_cam.MV_CC_ConvertPixelType(pstCvtParam)
            """
            if ret == MV_OK:
                print("Convert Pixel Type Success.")
            else:
                print("Convert Pixel Type failed",ret)
            """

        #ch: 将图片变为OpenCV可读类型 | en: convert image type to make it readable by OpenCV
        img0 = Color_numpy(buf_save_image,stFrameInfo.nWidth,stFrameInfo.nHeight) #先转成opencv格式的numpy数组图像格式
        img = cv2.resize(img0, None, fx=1/4, fy=1/4)

        

#枚举设备
enum_devices()
open_device()
threads = []

# 注意：这里传递的是函数对象，而不是调用函数
threadGrab = threading.Thread(target = start_grabbing)  
threads.append(threadGrab)
threadGrab.start()
threadShow = threading.Thread(target = work_thread) 
threads.append(threadShow)
threadShow.start()

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
def getImg():
    global img
    return img

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
#初始化本次运行视觉处理标准参数
count = 0
ok_count = 0
while True:
    #用户输入"q"停止服务
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    try:
        conn, addr = s.accept()     # 建立客户端连接
        print(f"客户端已连接: {addr}")

        while True:
            #用户输入"q"停止服务
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            try:
                data = conn.recv(8005)  # 接收数据
                if not data:  # 如果没有接收到数据，说明客户端已断开连接
                    print("客户端主动断开连接")
                    break

                data = data.decode() #对接受的数据解码
                print('接收到:', data)# 打印接收到的解码数据
                img_ori = getImg()
                if data == "ready":
                    txt = input("请输入信息，格式为 44.2,23.9,0.0\0D")
                    txt = txt.encode()
                    conn.send(txt)  # 发送消息给ABB工业机器人客户端
                #todo 学生作业请在下面生成图像处理代码，作业时请删除 pass
                elif data == "pic":
                    
                    #todo  读取一张图片
                    #frame = cap.read()  # 读取一帧图像
                    img = getImg()
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

cv2.destroyAllWindows()
