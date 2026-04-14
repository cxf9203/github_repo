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
import qdarkstyle.dark.resouce_rc as resouce_rc
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
            #YOLO_Predict(img)
            #doMeasure(img)


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


from ultralytics import YOLO
# Load your trained YOLO model
model =YOLO('torchModel/chilun.pt')
print(model.names)
#{0: 'chiquan', 1: 'dizuo', 2: 'gear'}
def YOLO_Predict(img):
    global model
    labelSet = ["chiquan", "", "dizuo","gear"]
    # 初始化计数器字典（只统计非空标签）
    counts = {}

    results = model.predict(source=img, save=False, show=False)
    #print(results)
    chilun_count =0 
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            labelidx = box.cls[0].item()
            label = labelSet[int(labelidx)]
            confidence = box.conf[0].item()

            # 统计标签数量（忽略空字符串标签）
            if label:
                counts[label] = counts.get(label, 0) + 1
            if labelidx==2:#齿轮数量+1
                chilun_count+=1
            # 绘制检测框和标签
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)


    if chilun_count == 4:
        print("OK，齿轮四个")
        flag = True
    else:
        print(f"NG (chilun 数量为 {chilun_count}，需要 4)")
        flag = False
    return flag,img
def doMeasure(img):
    flag = True

    global model
    labelSet = ["chiquan", "", "dizuo","gear"]
    # 初始化计数器字典（只统计非空标签）
    counts = {}

    results = model.predict(source=img, save=False, show=False)
    #print(results)

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            labelidx = box.cls[0].item()
            label = labelSet[int(labelidx)]
            confidence = box.conf[0].item()

            
            # 计算中心点坐标
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            # 绘制中心点
            cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)
            # 在中心点处添加标签
            cv2.putText(img, f"{label}", (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            # 在中心点处添加尺寸标签
            cv2.putText(img, f"{x2-x1}x{y2-y1}", (center_x, center_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            if x2-x1 >220 and y2-y1 > 220:
                flag = True
            else:   
                flag = False
                        
            # 绘制检测框和标签
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    return flag,img
    

# ==================== Socket线程 ====================
def socket_work(window):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #host = socket.gethostname()
    host = "192.168.101.98"
    port = 8005
    s.bind((host, port))
    
    s.listen(1)

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
            
            if msg == "dizuo":
                img = window.latest_img

                if img is None:
                    conn.send(b"none")
                    continue

                #result = isRedcolor(img)
                result,result_img = doMeasure(img)#测量尺寸
                h, w = result_img.shape[:2]
                qimg = QImage(result_img.data, w, h, 3 * w, QImage.Format_BGR888)
                pixmap = QPixmap.fromImage(qimg)
                window.label_3.setPixmap(
                    pixmap.scaled(window.label_3.size(), Qt.KeepAspectRatio)
                )
                if result:
                    conn.send(b"ok")#继续
                else:
                    conn.send(b"ng")#停止肥料
            elif msg == "chilun":
                img = window.latest_img

                if img is None:
                    conn.send(b"none")
                    continue

                result,result_img = YOLO_Predict(img)#检测齿轮 外圈
                h, w = result_img.shape[:2]
                qimg = QImage(result_img.data, w, h, 3 * w, QImage.Format_BGR888)
                pixmap = QPixmap.fromImage(qimg)
                window.label_3.setPixmap(
                    pixmap.scaled(window.label_3.size(), Qt.KeepAspectRatio)
                )
                if result:
                    conn.send(b"ok")
                else:
                    conn.send(b"ng")
            else:
                conn.send(b"ok")

        conn.close()

def load_qss(app):
    with open("qdarkstyle/dark/darkstyle.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())
# ==================== 主程序 ====================
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 加载QSS
    load_qss(app)
    main_window = MainWindow()
    
    main_window.show()

    # socket线程
    sock_thread = QThread()
    sock_thread.run = lambda: socket_work(main_window)
    sock_thread.start()

    sys.exit(app.exec())