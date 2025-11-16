# 串口设备库
import serial
from serial.tools import list_ports

# 类型相关
from dataclasses import dataclass, field
from typing import List, Union

# 线程相关
import queue
import threading

# 检测数据类
@dataclass
class UartData:
    device: str# 设备名
    description: str# 设备描述

# 检测结果类
@dataclass
class UartListResult:
    list: List[UartData]=field(default_factory=list)


# 列出串口
def list_uart() -> UartListResult:
    # 获取端口列表
    ports=list_ports.comports()
    # 构建结果
    result=UartListResult()
    # 遍历端口
    for port in ports:
        uart=UartData(device=port.device, description=port.description)
        result.list.append(uart)
        print(f"设备名：{port.device} 设备描述:{port.description}")
    return result


# 串口实例
class UartIns:

    # 实例初始化
    def __init__(self):
        # 串口属性
        self.name:str=None
        self.buadrate:int=None
        self.uart:serial.Serial=None
        # 发送属性
        self.send_queue=None
        self.send_thread=None

    # 发送线程
    def _send_thread(self):
        while True:
            # 等待数据
            data=self.send_queue.get()
            # 结束信号
            if data is None:
                break
            # 发送数据
            if self.uart.is_open:
                self.uart.flush()
                self.uart.write(data)
                print("发送数据:",data)
        
    # 串口初始化
    def init(self,name:str,baudrate:int=115200) -> bool:
        try:
            # 串口属性
            self.name=name
            self.buadrate=baudrate
            self.uart=serial.Serial(
                port=self.name,
                baudrate=self.buadrate,
            )
            # 发送属性
            self.send_queue=queue.Queue()
            self.send_thread=threading.Thread(target=self._send_thread,daemon=True)
            self.send_thread.start()
            print(f"串口初始化成功")
            return True
        except:
            print(f"串口初始化失败")
            return False

    # 串口反初始化
    def deinit(self):
        # 回收串口
        self.uart.close()
        self.name=None
        self.buadrate=None
        self.uart=None
        # 回收发送线程
        self.send_queue.put(None)
        self.send_thread.join()
        self.send_queue=None
        print(f"串口反初始化成功")

    # 串口阻塞发送自动数据
    def sendauto_block(self,data: Union[bytes,str]):
        if self.uart.is_open:
            if isinstance(data, bytes):
                self.uart.flush()
                self.uart.write(data)
            elif isinstance(data, str):
                self.uart.flush()
                self.uart.write(data.encode('utf-8'))
            else:
                raise TypeError("无效的类型")
    
    # 串口非阻塞发送自动数据
    def sendauto_unblock(self,data: Union[bytes,str]):
        if self.uart.is_open:
            if isinstance(data, bytes):
                self.send_queue.put(data)
            elif isinstance(data, str):
                self.send_queue.put(data.encode('utf-8'))
            else:
                raise TypeError("无效的类型")
    
