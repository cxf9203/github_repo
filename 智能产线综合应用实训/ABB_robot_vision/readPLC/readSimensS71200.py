#这个脚本为读取西门子 s7 1200 PLC数据脚本
#PLC ip地址为192.168.101.33
#PLC  rack=0, slot=2
#PLC  DB1
#DB1.0  机器人1的实时数量
#DB1.4  机器人1的良品数量
#DB1.8  机器人1的工作状态
#DB1.12 机器人1的节拍时间
#DB1.16 机器人2的实时数量

import snap7
import time

# 创建一个PLC对象   

plc = snap7.client.Client() 
plc.connect('192.168.101.33', 0, 2) #连接PLC

while True:
    #读取PLC DB1.0  机器人1的实时数量
    real_product_number = plc.read_area(snap7.types.Areas.DB, 1, 0, 4)
    real_product_number = int.from_bytes(real_product_number, byteorder='big')
    print("机器人1的实时数量：", real_product_number)
    #读取PLC DB1.4  机器人1的良品数量
    good_product_number = plc.read_area(snap7.types.Areas.DB, 1, 4, 4)
    good_product_number = int.from_bytes(good_product_number, byteorder='big')

    print("机器人1的良品数量：", good_product_number)
    #读取PLC DB1.8  机器人1的工作状态
    working_state = plc.read_area(snap7.types.Areas.DB, 1, 8, 1)
    working_state = int.from_bytes(working_state, byteorder='big')
    print("机器人1的工作状态：", working_state)

    #读取PLC DB1.12 机器人1的节拍时间   
    cycle_time = plc.read_area(snap7.types.Areas.DB, 1, 12, 4)
    cycle_time = int.from_bytes(cycle_time, byteorder='big')
    print("机器人1的节拍时间：", cycle_time)

    #读取PLC DB1.16 机器人2的实时数量
    real_product_number2 = plc.read_area(snap7.types.Areas.DB, 1, 16, 4)
    real_product_number2 = int.from_bytes(real_product_number2, byteorder='big')
    print("机器人2的实时数量：", real_product_number2)

    time.sleep(1)
    #关闭连接