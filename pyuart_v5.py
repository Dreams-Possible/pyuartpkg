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
        print(f"device: {port.device} && description: {port.description}")
    return result


# 串口实例
class UartIns:

    # 实例初始化
    def __init__(self):
        # 串口状态
        self.state=0
        # 串口属性
        self.name:str=None
        self.buadrate:int=None
        self.uart:serial.Serial=None
        # 发送属性
        self.send_queue:queue.Queue=None
        self.send_thread:threading.Thread=None

    # 串口发送线程
    def _send_thread(self):
        while self.state:
            # 等待数据
            data=self.send_queue.get()
            # 退出信号
            if data is None:
                break
            # 发送数据
            if self.uart.is_open:
                while self.uart.out_waiting:
                    self.uart.flush()
                self.uart.write(data)

    # 串口初始化
    def init(self,name:str,baudrate:int=115200) -> bool:
        try:
            # 串口状态
            self.state=1
            # 串口属性
            self.name=name
            self.buadrate=baudrate
            self.uart=serial.Serial(
                port=self.name,
                baudrate=self.buadrate,
            )
            self.state=1
            # 发送属性
            self.send_queue=queue.Queue()
            self.send_thread=threading.Thread(target=self._send_thread,daemon=True)
            self.send_thread.start()
            print(f"device: {self.name} init done")
            return True
        except:
            print(f"device: {self.name} init failed")
            return False

    # 串口反初始化
    def deinit(self):
        # 串口状态
        self.state=0
        # 回收发送线程
        self.send_queue.put(None)
        self.send_thread.join()
        self.send_thread=None
        self.send_queue=None
        # 回收串口
        self.uart.close()
        self.name=None
        self.buadrate=None
        self.uart=None
        print(f"device: {self.name} deinit done")

    # 串口阻塞发送数据
    def send_block(self,data: bytes):
        if self.uart.is_open:
            if isinstance(data, bytes):
                while self.uart.out_waiting:
                    self.uart.flush()
                self.uart.write(data)
            else:
                raise TypeError("invalid type")
    
    # 串口发送数据
    def send(self,data: bytes):
        if self.uart.is_open:
            if isinstance(data, bytes):
                self.send_queue.put(data)
            else:
                raise TypeError("invalid type")
            
    # 串口接收数据
    def recv(self) -> bytes:
        if self.uart.is_open:
            # 检查接收
            if self.uart.in_waiting:
                # 读取数据
                data = self.uart.read(self.uart.in_waiting)
                return data
            else:
                return None

# 串口通信实例
class UartComuIns():

    # 实例初始化
    def __init__(self):
        # 标志位
        self.HEAD=ord('A')  #包头
        self.TAIL=ord('Z')  #包尾
        self.ESCAPE=ord('_')  #转义
        # 串口实例
        self.uart:UartIns=None

    # 串口通信初始化
    def init(self,uart:UartIns):
        self.uart=uart

    # 构造包
    def _mkpkg(self,data: bytes) -> bytes:
        # 检查数据类型
        if not isinstance(data,bytes):
            raise TypeError("data must be bytes")
        # 转义
        escaped = bytearray()
        for b in data:
            # 包头
            if b == self.HEAD:
                escaped.extend([self.ESCAPE, self.HEAD])
            # 包尾
            elif b == self.TAIL:
                escaped.extend([self.ESCAPE, self.TAIL])
            # 转译
            elif b == self.ESCAPE:
                escaped.extend([self.ESCAPE, self.ESCAPE])
            else:
                escaped.append(b)
        # 构造
        return bytes([self.HEAD]) + bytes(escaped) + bytes([self.TAIL])
    
    # 解包
    def _dcpkg(self,pkg: bytes) -> bytes:
        # 检查包头包尾
        if pkg[0] != self.HEAD or pkg[-1] != self.TAIL:
            raise TypeError("bad packet header or tail")
        # 提取包
        payload = pkg[1:-1]
        decoded = bytearray()
        # 反转义
        i = 0
        while i < len(payload):
            b = payload[i]
            # 检查转义标志
            if b == self.ESCAPE:
                i += 1
                # 转义长度异常
                if i >= len(payload):
                    raise TypeError("incomplete escape sequence")
                # 检查转义内容
                next_b = payload[i]
                # 包头
                if next_b == self.HEAD:
                    decoded.append(self.HEAD)
                # 包尾
                elif next_b == self.TAIL:
                    decoded.append(self.TAIL)
                # 转义
                elif next_b == self.ESCAPE:
                    decoded.append(self.ESCAPE)
                # 转义内容异常
                else:
                    raise TypeError("invalid escape sequence")
            else:
                decoded.append(b)
            i += 1
        return bytes(decoded)

    # 串口通信发送
    def send(self,data):
        # 类型
        try:
            data=bytes(data)
        except:
            raise TypeError("can not convert to bytes")
        # 构造包
        data=self._mkpkg(data)
        # 发送
        self.uart.send(data)

    # 串口通信接收
    def recv(self) -> bytes:
        # 接收
        data = self.uart.recv()
        print("Raw received data:", data)
        # 检查是否有数据
        if data is None:
            return None
        else:
            # 解包
            data=self._dcpkg(data)
            return data
        

