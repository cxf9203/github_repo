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
model =YOLO(f'torchModel/lunxi.pt')
print(model.names)
#{0: 'dingxiao', 1: 'jilun', 2: 'waike'}
def YOLO_Predict(img):
    global model
    labelSet = ["dingxiao", "", "jilun","waike"]
    # 初始化计数器字典（只统计非空标签）
    counts = {}

    results = model.predict(source=img, save=True, show=True)
    print(results)

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

            # 绘制检测框和标签
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{label} {confidence:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # 打印统计结果
    print("检测到的标签数量统计:")
    for label, count in counts.items():
        print(f"{label}: {count}")
    # 判断 chilun 数量是否为 4
    chilun_count = counts.get("chilun", 0)
    if chilun_count == 4:
        print("OK")
        flag = True
    else:
        print(f"NG (chilun 数量为 {chilun_count}，需要 4)")
        flag = False
    return flag
def doMeasure(img):
    # ---------------------- 1. 图像读取与预处理 ----------------------
    # 读取图像（替换为你的图片路径）
    img = cv2.imread('torchModel/gear.bmp', cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("无法读取图像，请检查路径")

    # 高斯滤波去噪，减少轮廓检测的干扰
    blur = cv2.GaussianBlur(img, (5, 5), 0)

    # 自适应二值化，适配光照不均的情况
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # 形态学操作，去除小噪点，闭合齿轮轮廓
    kernel = np.ones((3, 3), np.uint8)
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel, iterations=1)

    # ---------------------- 2. 轮廓检测与筛选 ----------------------
    # 提取所有轮廓
    contours, hierarchy = cv2.findContours(
        morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    cv2.drawContours(img, contours, -1, (0, 255, 0), 2) # 绘制所有轮廓（可选）
    
    # 筛选齿轮轮廓（过滤过小/过大的噪点轮廓）
    gear_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # 面积阈值，根据你的图像尺寸调整（这里适配示例图）
        if 5000 < area < 50000:
            gear_contours.append(cnt)

    # 按轮廓面积排序：最大的是齿圈，中间4个是行星轮，最小的是中心太阳轮
    gear_contours = sorted(gear_contours, key=cv2.contourArea, reverse=True)
    ring_gear = gear_contours[0]  # 最外层齿圈
    planet_gears = gear_contours[1:5]  # 4个行星轮
    #sun_gear = gear_contours[5]  # 中心太阳轮（如果存在）

    # ---------------------- 3. 齿轮参数计算 ----------------------
    def calculate_gear_params(contour, gear_name):
        """计算单个齿轮的尺寸参数"""
        # 1. 外接圆（齿顶圆）参数
        (x, y), radius = cv2.minEnclosingCircle(contour)
        center = (int(x), int(y))
        tip_diameter = 2 * radius  # 齿顶圆直径（齿轮总大小）
        
        # 2. 内接圆（齿根圆）参数（通过凸包近似）
        hull = cv2.convexHull(contour, returnPoints=True)
        (hx, hy), hull_radius = cv2.minEnclosingCircle(hull)
        root_diameter = 2 * hull_radius  # 齿根圆直径
        
        # 3. 齿数计算（通过轮廓的角点/凸缺陷计数）
        # 方法1：凸缺陷计数（适合齿轮齿形）
        hull_idx = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, hull_idx)
        tooth_count = 0
        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                # 深度阈值，过滤非齿形的凹陷
                if d > 1000:
                    tooth_count += 1
        
        # 4. 轮廓周长、面积
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        
        # 打印参数
        print(f"=== {gear_name} 参数 ===")
        print(f"齿顶圆直径: {tip_diameter:.2f} 像素")
        print(f"齿根圆直径: {root_diameter:.2f} 像素")
        print(f"齿数: {tooth_count}")
        print(f"轮廓周长: {perimeter:.2f} 像素")
        print(f"轮廓面积: {area:.2f} 像素²\n")
        
        return center, radius, tip_diameter, tooth_count

    # 计算齿圈参数
    ring_center, ring_radius, ring_tip_dia, ring_teeth = calculate_gear_params(ring_gear, "齿圈")
    #绘制齿圈
    cv2.circle(img, ring_center, int(ring_radius), (0, 0, 255), 2)
    
    # 计算4个行星轮参数
    planet_params = []
    for i, pg in enumerate(planet_gears):
        params = calculate_gear_params(pg, f"行星轮 {i+1}")
        planet_params.append(params)

    # 计算太阳轮参数（如果存在）
    # if len(gear_contours) >= 6:
    #     sun_center, sun_radius, sun_tip_dia, sun_teeth = calculate_gear_params(sun_gear, "太阳轮")

    # ---------------------- 4. 结果可视化 ----------------------
    # 转彩色图用于标注
    img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # 绘制齿圈
    cv2.circle(img_color, ring_center, int(ring_radius), (0, 0, 255), 2)
    cv2.putText(img_color, f"齿圈 D={ring_tip_dia:.1f}px 齿数={ring_teeth}",
                (ring_center[0]-150, ring_center[1]-ring_radius-20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # 绘制行星轮
    colors = [(0, 255, 0), (255, 0, 0), (255, 255, 0), (0, 255, 255)]
    for i, (center, radius, dia, teeth) in enumerate(planet_params):
        cv2.circle(img_color, center, int(radius), colors[i], 2)
        cv2.putText(img_color, f"行星轮{i+1} D={dia:.1f}px 齿数={teeth}",
                    (center[0]-80, center[1]-int(radius)-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2)

    # 绘制太阳轮
    # if len(gear_contours) >= 6:
    #     cv2.circle(img_color, sun_center, int(sun_radius), (255, 0, 255), 2)
    #     cv2.putText(img_color, f"太阳轮 D={sun_tip_dia:.1f}px 齿数={sun_teeth}",
    #                 (sun_center[0]-80, sun_center[1]-int(sun_radius)-15),
    #                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

    # 保存并显示结果
    cv2.imwrite('gear_measurement_result.png', img_color)
    return img_color

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

                #result = isRedcolor(img)
                result_img = doMeasure(img)
                
                # 将结果图像显示到label_3上
                if result_img is not None:
                    h, w = result_img.shape[:2]
                    qimg = QImage(result_img.data, w, h, 3 * w, QImage.Format_BGR888)
                    pixmap = QPixmap.fromImage(qimg)
                    window.label_3.setPixmap(
                        pixmap.scaled(window.label_3.size(), Qt.KeepAspectRatio)
                    )
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