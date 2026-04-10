# -- coding: utf-8 --
import sys
import time
import socket
import sqlite3
import numpy as np
import cv2

from ctypes import *

from MvImport.CamOperation_class import *
from MvImport.MvCameraControl_class import *
from MvImport.MvErrorDefine_const import *
from MvImport.CameraParams_header import *

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QImage, QPixmap

from mainUI import Ui_MainWindow


# ==================== 全局变量 ====================
deviceList = MV_CC_DEVICE_INFO_LIST()
cam = MvCamera()
obj_cam_operation = None


# ==================== 相机初始化 ====================
def enum_devices():
    global deviceList
    ret = MvCamera.MV_CC_EnumDevices(MV_GIGE_DEVICE | MV_USB_DEVICE, deviceList)
    if ret != 0 or deviceList.nDeviceNum == 0:
        print("未找到相机")
        return False
    print("找到设备:", deviceList.nDeviceNum)
    return True


def open_device():
    global obj_cam_operation
    obj_cam_operation = CameraOperation(cam, deviceList, 0)
    ret = obj_cam_operation.Open_device()
    if ret != 0:
        print("打开失败")
        return False
    return True


def start_grabbing():
    obj_cam_operation.obj_cam.MV_CC_StartGrabbing()


# ==================== QThread采集线程 ====================
class CameraThread(QThread):
    image_signal = Signal(object)

    def __init__(self, cam_op):
        super().__init__()
        self.cam_op = cam_op
        self.running = True

    def run(self):
        stFrameInfo = MV_FRAME_OUT_INFO_EX()
        stPayloadSize = MVCC_INTVALUE_EX()

        while self.running:
            ret = self.cam_op.obj_cam.MV_CC_GetIntValueEx("PayloadSize", stPayloadSize)
            if ret != MV_OK:
                continue

            size = int(stPayloadSize.nCurValue)

            if self.cam_op.buf_grab_image_size < size:
                self.cam_op.buf_grab_image = (c_ubyte * size)()
                self.cam_op.buf_grab_image_size = size

            ret = self.cam_op.obj_cam.MV_CC_GetOneFrameTimeout(
                self.cam_op.buf_grab_image,
                self.cam_op.buf_grab_image_size,
                stFrameInfo
            )

            if ret != MV_OK:
                continue

            # 转BGR
            if stFrameInfo.enPixelType != PixelType_Gvsp_BGR8_Packed:
                convert_param = MV_CC_PIXEL_CONVERT_PARAM()
                convert_param.nWidth = stFrameInfo.nWidth
                convert_param.nHeight = stFrameInfo.nHeight
                convert_param.pSrcData = self.cam_op.buf_grab_image
                convert_param.nSrcDataLen = stFrameInfo.nFrameLen
                convert_param.enSrcPixelType = stFrameInfo.enPixelType
                convert_param.enDstPixelType = PixelType_Gvsp_BGR8_Packed

                size = stFrameInfo.nWidth * stFrameInfo.nHeight * 3
                buf = (c_ubyte * size)()
                convert_param.pDstBuffer = buf
                convert_param.nDstBufferSize = size

                ret = self.cam_op.obj_cam.MV_CC_ConvertPixelType(convert_param)
                if ret != MV_OK:
                    continue
            else:
                buf = self.cam_op.buf_grab_image

            img = Color_numpy(buf, stFrameInfo.nWidth, stFrameInfo.nHeight)

            self.image_signal.emit(img)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# ==================== 图像算法 ====================
def isRedcolor(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([170, 100, 100])
    upper2 = np.array([180, 255, 255])

    mask = cv2.inRange(hsv, lower1, upper1) + cv2.inRange(hsv, lower2, upper2)

    return np.any(mask)
def YOLO_Predict(img):
    pass

# ==================== UI ====================
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("视觉检测系统")

        self.latest_img = None

        # 初始化相机
        enum_devices()
        open_device()
        start_grabbing()

        # 启动线程
        self.cam_thread = CameraThread(obj_cam_operation)
        self.cam_thread.image_signal.connect(self.update_image)
        self.cam_thread.start()

    def update_image(self, img):
        self.latest_img = img
        self.display_image(img)

    def display_image(self, img):
        if img is None:
            return

        h, w = img.shape[:2]
        qimg = QImage(img.data, w, h, 3 * w, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qimg)
        self.label.setPixmap(
            pixmap.scaled(self.label.size(), Qt.KeepAspectRatio)
        )


# ==================== Socket线程 ====================
def socket_work(window):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #host = socket.gethostname()
    host = "192.168.1.3"
    port = 8005
    s.bind((host, port))
    s.listen(5)

    print("Socket启动")

    while True:
        conn, addr = s.accept()
        print("连接:", addr)

        while True:
            data = conn.recv(1024)
            if not data:
                break

            msg = data.decode()
            print("收到:", msg)
            
            if msg == "pic":
                img = window.latest_img

                if img is None:
                    conn.send(b"none")
                    continue

                result = isRedcolor(img)

                if result:
                    conn.send(b"ok")
                else:
                    conn.send(b"ng")
            elif msg == "yolo":
                img = window.latest_img

                if img is None:
                    conn.send(b"none")
                    continue

                result = YOLO_Predict(img)
                if result:
                    conn.send(b"ok")
                else:
                    conn.send(b"ng")
            else:
                conn.send(b"ok")

        conn.close()


# ==================== 主程序 ====================
if __name__ == '__main__':
    app = QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    # socket线程
    sock_thread = QThread()
    sock_thread.run = lambda: socket_work(main_window)
    sock_thread.start()

    sys.exit(app.exec())