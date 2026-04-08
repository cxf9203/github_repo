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
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap
from mainUI import Ui_MainWindow

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

"""连接数据库day4"""
# 数据库文件名 #todo 修改为你的数据库地址
db_file = 'D:/github_repo/智能产线综合应用实训/line/myproject/db.sqlite3'

Stand_color = "RED"
Stand_shape = "CIRCLE"


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

# ==================== UI类 ====================
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # 设置UI
        self.setWindowTitle("海康相机视觉检测系统")

        # 初始化为空图像
        self.display_image(None)

    def display_image(self, cv_img):
        """在label上显示OpenCV图像"""
        if cv_img is None:
            # 显示空白图像
            blank = np.zeros((371, 401, 3), dtype=np.uint8)
            qimg = QImage(blank.data, blank.shape[1], blank.shape[0], 
                         blank.shape[1] * 3, QImage.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(qimg))
        else:
            # 将OpenCV图像转换为QImage
            height, width = cv_img.shape[:2]
            bytes_per_line = 3 * width
            qimg = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_BGR888)

            # 缩放图像以适应label大小，保持宽高比
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(self.label.size(), 
                                         Qt.KeepAspectRatio, 
                                         Qt.SmoothTransformation)
            self.label.setPixmap(scaled_pixmap)

    def update_image(self, cv_img):
        """从后台线程接收图像并更新显示"""
        self.display_image(cv_img)

# ==================== 后台线程类 ====================
class CameraThread(QThread):
    """相机采集线程"""
    image_ready = Signal(np.ndarray)  # 图像准备好信号

    def run(self):
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

            ret = obj_cam_operation.obj_cam.MV_CC_GetOneFrameTimeout(obj_cam_operation.buf_grab_image, 
                                                                    obj_cam_operation.buf_grab_image_size, 
                                                                    stFrameInfo)

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

            #ch: 将图片变为OpenCV可读类型 | en: convert image type to make it readable by OpenCV
            img = Color_numpy(buf_save_image, stFrameInfo.nWidth, stFrameInfo.nHeight)
            # 发送图像到主线程
            self.image_ready.emit(img)


class SocketThread(QThread):
    """Socket通信线程"""
    image_ready = Signal(np.ndarray)  # 图像准备好信号

    def run(self):
        global img
        # 创建socket对象并设置选项
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = socket.gethostname()
        port = 8005
        print(host)
        s.bind((host, port))
        print(s)
        s.listen(30)

        print("等待客户端连接...")
        count = 0
        ok_count = 0

        while True:
            try:
                conn, addr = s.accept()
                print(f"客户端已连接: {addr}")

                while True:
                    try:
                        data = conn.recv(8005)
                        if not data:
                            print("客户端主动断开连接")
                            break

                        data = data.decode()
                        print('接收到:', data)
                        img_ori = getImg()

                        if data == "ready":
                            txt = input("请输入信息，格式为 44.2,23.9,0.0\0D")
                            txt = txt.encode()
                            conn.send(txt)

                        elif data == "pic":#TODO 修改完善识别任务，当前是isRedcolor()例子。
                            img = getImg()
                            result = isRedcolor(img)

                            # 发送图像到主线程显示
                            self.image_ready.emit(img)

                            if result == True:
                                res = "red"
                                res = res.encode()
                                conn.send(res)
                            else:
                                res = "not"
                                res = res.encode()
                                conn.send(res)

                                # # 插入数据库
                                # try:
                                #     if count == 0:
                                #         rate = 0.0
                                #     else:
                                #         rate = ok_count / count

                                #     conn_db = sqlite3.connect(db_file)
                                #     cursor = conn_db.cursor()
                                #     sql = "INSERT INTO myline_workinghistory (device_id_id,number_history, good_number) VALUES (?, ?, ?)"
                                #     cursor.execute(sql, (1, count, ok_count))
                                #     conn_db.commit()
                                #     conn_db.close()
                                # except sqlite3.Error as e:
                                #     print(f"数据库插入错误: {e}")

                        else:
                            str_msg = 'hello ABBrobotware    '
                            str_msg = str_msg.encode()
                            conn.send(str_msg)

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
                    conn.close()
                    print("连接已关闭")
                except:
                    pass

        try:
            s.close()
        except:
            pass



# ==================== 主程序 ====================
if __name__ == '__main__':
    #初始化本次运行视觉处理标准参数
    count = 0
    ok_count = 0
    # 枚举设备
    enum_devices()
    open_device()

    # 创建Qt应用
    app = QApplication([])

    # 创建主窗口
    main_window = MainWindow()
    

    # 创建并启动相机采集线程
    camera_thread = CameraThread()
    camera_thread.image_ready.connect(main_window.update_image)
    camera_thread.start()

    # 创建并启动socket通信线程
    socket_thread = SocketThread()
    socket_thread.image_ready.connect(main_window.update_image)
    socket_thread.start()
    #显示界面
    main_window.show()
    # 启动相机取流
    start_grabbing()

    # 运行Qt应用主循环
    app.exec_()

    # 程序退出时清理资源
    stop_grabbing()
    close_device()
    cv2.destroyAllWindows()


