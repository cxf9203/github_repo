# -- coding: utf-8 --

from MvImport.CamOperation_class import *
from MvImport.MvCameraControl_class import *
from MvImport.MvErrorDefine_const import *
from MvImport.CameraParams_header import *

import cv2
import numpy as np
import threading

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


if __name__ == "__main__":

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

            # 设定黄色的阈值    
            imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            lower_HSV=np.array([ 15, 100,  50])
            upper_HSV=np.array([ 35, 255, 255])
            mask = cv2.inRange(imgHSV, lower_HSV, upper_HSV)

            kernel = np.ones((5,5), dtype=int)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            max_contours = max(contours, key=cv2.contourArea)
            M = cv2.moments(max_contours)
            if M["m00"] == 0:
                return None
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cv2.drawContours(img, contours, -1, (0,255,0), 3)
            cv2.circle(img, (cx, cy), 5, (0,255,0), -1)
            cv2.putText(img, f'({cx},{cy})', (cx-80, cy-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            cv2.imshow("result",img)

            k = cv2.waitKey(100)
            if k==27:
                break

    
    enum_devices()
    open_device()
    threads = []
    threadGrab = threading.Thread(target = start_grabbing())  
    threads.append(threadGrab)
    threadGrab.start()
    threadShow = threading.Thread(target = work_thread()) 
    threads.append(threadShow)
    threadShow.start()

    for t in threads:
        t.join()

    cv2.destroyAllWindows()
   