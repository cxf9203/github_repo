#采集ABB工业机器人六轴数据与I/O状态

import clr
import os
#from System import Array
# 添加ABB PC SDK引用
# 假设ABB PC SDK安装在默认路径
sdk_path = "D:/abb/Bin/ABB.Robotics.Controllers.PC.dll"
if os.path.exists(sdk_path):
    clr.AddReference(sdk_path)
else:
    print(f"无法找到ABB PC SDK: {sdk_path}")
    exit(1)
# 添加ABB PC SDK引用
clr.AddReference("ABB.Robotics.Controllers")
clr.AddReference("ABB.Robotics.Controllers.PC")

from ABB.Robotics.Controllers import ControllerFactory, ControllerInfo
from ABB.Robotics.Controllers.RapidDomain import RobData, UserData, NumData, BoolData

class ABBRobotDataCollector:
    def __init__(self):
        self.controller = None
        self.connected = False
        
    def connect(self, ip_address=None):
        """连接到ABB机器人控制器"""
        try:
            if ip_address:
                # 通过IP地址连接
                self.controller = ControllerFactory.CreateFrom(ip_address)
            else:
                # 自动发现并连接到第一个可用控制器
                self.controller = ControllerFactory.CreateFrom(ControllerInfo.GetControllers()[0])
            
            self.connected = True
            print("成功连接到ABB机器人控制器")
            return True
        except Exception as e:
            print(f"连接失败: {str(e)}")
            return False
    
    def disconnect(self):
        """断开与机器人控制器的连接"""
        if self.controller:
            self.controller.Dispose()
            self.controller = None
            self.connected = False
            print("已断开与机器人控制器的连接")
    
    def get_joint_positions(self):
        """获取六轴关节位置数据"""
        if not self.connected:
            print("未连接到机器人控制器")
            return None
            
        try:
            # 获取机器人运动设备
            motion_device = self.controller.MotionSystem.ActiveMotionDevice
            # 获取关节位置
            joints = motion_device.GetJoints()
            
            # 转换为Python列表
            joint_positions = [joints.GetJoint(i) for i in range(6)]
            
            return joint_positions
        except Exception as e:
            print(f"获取关节位置失败: {str(e)}")
            return None
    
    def get_io_signals(self):
        """获取I/O信号状态"""
        if not self.connected:
            print("未连接到机器人控制器")
            return None
            
        try:
            # 获取I/O系统
            io_system = self.controller.IOSystem
            
            # 获取所有数字输入信号
            digital_inputs = {}
            for signal in io_system.GetSignals("DI"):
                digital_inputs[signal.Name] = signal.Value
                
            # 获取所有数字输出信号
            digital_outputs = {}
            for signal in io_system.GetSignals("DO"):
                digital_outputs[signal.Name] = signal.Value
                
            # 获取所有组输入信号
            group_inputs = {}
            for signal in io_system.GetSignals("GI"):
                group_inputs[signal.Name] = signal.Value
                
            # 获取所有组输出信号
            group_outputs = {}
            for signal in io_system.GetSignals("GO"):
                group_outputs[signal.Name] = signal.Value
                
            # 获取所有模拟输入信号
            analog_inputs = {}
            for signal in io_system.GetSignals("AI"):
                analog_inputs[signal.Name] = signal.Value
                
            # 获取所有模拟输出信号
            analog_outputs = {}
            for signal in io_system.GetSignals("AO"):
                analog_outputs[signal.Name] = signal.Value
                
            return {
                "digital_inputs": digital_inputs,
                "digital_outputs": digital_outputs,
                "group_inputs": group_inputs,
                "group_outputs": group_outputs,
                "analog_inputs": analog_inputs,
                "analog_outputs": analog_outputs
            }
        except Exception as e:
            print(f"获取I/O信号失败: {str(e)}")
            return None
    
    def get_rapid_variable(self, variable_name, module_name="T_ROB1"):
        """获取RAPID变量值"""
        if not self.connected:
            print("未连接到机器人控制器")
            return None
            
        try:
            # 获取RAPID任务
            rapid_task = self.controller.Rapid.GetTask(module_name)
            
            # 获取RAPID数据
            rapid_data = rapid_task.GetData(variable_name)
            
            # 根据变量类型获取值
            if isinstance(rapid_data, NumData):
                return rapid_data.Value
            elif isinstance(rapid_data, BoolData):
                return rapid_data.Value
            elif isinstance(rapid_data, RobData):
                return rapid_data.ToString()
            else:
                return rapid_data.ToString()
        except Exception as e:
            print(f"获取RAPID变量失败: {str(e)}")
            return None

# 使用示例
if __name__ == "__main__":
    collector = ABBRobotDataCollector()
    
    # 连接到机器人控制器 (替换为你的机器人IP地址)
    if collector.connect("192.168.0.100"):
        try:
            # 获取关节位置
            joint_positions = collector.get_joint_positions()
            if joint_positions:
                print("关节位置 (度):")
                for i, pos in enumerate(joint_positions):
                    print(f"轴{i+1}: {pos:.2f}°")
            
            # 获取I/O状态
            io_signals = collector.get_io_signals()
            if io_signals:
                print("\n数字输入信号:")
                for name, value in io_signals["digital_inputs"].items():
                    print(f"{name}: {value}")
                
                print("\n数字输出信号:")
                for name, value in io_signals["digital_outputs"].items():
                    print(f"{name}: {value}")
                
                print("\n模拟输入信号:")
                for name, value in io_signals["analog_inputs"].items():
                    print(f"{name}: {value}")
                
                print("\n模拟输出信号:")
                for name, value in io_signals["analog_outputs"].items():
                    print(f"{name}: {value}")
            
            # 获取RAPID变量
            variable_value = collector.get_rapid_variable("my_variable")
            if variable_value is not None:
                print(f"\nRAPID变量值: {variable_value}")
                
        finally:
            # 断开连接
            collector.disconnect()
