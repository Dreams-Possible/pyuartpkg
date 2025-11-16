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
        print(f"device: {port.device} description: {port.description}")
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
        # 接收属性
        self.recv_queue:queue.Queue=None
        self.recv_thread:threading.Thread=None

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
                self.uart.flush()
                self.uart.write(data)

    # 串口接收发送线程
    def _recv_thread(self):
        while self.state:
            # 检查接收
            if self.uart.in_waiting:
                # 读取数据
                data = self.uart.read(self.uart.in_waiting)
                # 发送数据
                self.recv_queue.put(data)

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
            # 接收属性
            self.recv_queue=queue.Queue()
            self.recv_thread=threading.Thread(target=self._recv_thread,daemon=True)
            self.recv_thread.start()
            print(f"init done")
            return True
        except:
            print(f"init failed")
            return False

    # 串口反初始化
    def deinit(self):
        # 串口状态
        self.state=0
        # 回收接收线程
        self.recv_thread.join()
        self.recv_thread=None
        self.recv_queue=None
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
        print(f"deinit done")

    # 串口阻塞发送数据
    def send_block(self,data: Union[bytes,str]):
        if self.uart.is_open:
            if isinstance(data, bytes):
                self.uart.flush()
                self.uart.write(data)
            elif isinstance(data, str):
                self.uart.flush()
                self.uart.write(data.encode('utf-8'))
            else:
                raise TypeError("invalid type")
    
    # 串口发送数据
    def send(self,data: Union[bytes,str]):
        if self.uart.is_open:
            if isinstance(data, bytes):
                self.send_queue.put(data)
            elif isinstance(data, str):
                self.send_queue.put(data.encode('utf-8'))
            else:
                raise TypeError("invalid type")
            
    # 串口阻塞接收数据
    def recv(self) -> bytes:
        if self.uart.is_open:
            data=self.recv_queue.get()
            return data

# 打包库
import struct

# 串口通信实例
class UartComuIns():

    # 实例初始化
    def __init__(self):
        # 标志位
        self.HEAD=0XAA
        self.TAIL=0X55
        self.ESCAPE=0x7D
        # 串口实例
        self.uart:UartIns=None

    # 串口通信初始化
    def init(self,name:UartIns):
        self.uart=name

    # 构造包
    def _mkpkg(self,data: List[int],bit: int = 16) -> bytes:
        # 匹配格式
        fmt = {8: "B", 16: "H", 32: "I", 64: "Q"}
        if bit not in fmt:
            raise TypeError("bit must be one of 8,16,32,64")
        # 构造包头
        headflag = struct.pack("<H", self.HEAD)
        # 构造包尾
        tailflag = struct.pack("<H", self.TAIL)
        # 构造包
        fmt = "<" + fmt[bit] * len(data)
        # 构造包体
        payload = struct.pack(fmt, *data)
        return headflag + payload + tailflag
    
    # 解包
    def _dcpkg(self,pkg: bytes,bit: int = 16) -> List[int]:
        # 包头包尾
        HEAD=0XAA55
        TAIL=0XAA55
        # 检查长度
        if len(pkg) < 4:
            raise TypeError("pkg too short")
        # 检查包头
        if struct.unpack_from("<H", pkg, 0)[0] != HEAD:
            raise TypeError("bad header")
        # 检查包尾
        if struct.unpack_from("<H", pkg, len(pkg) - 2)[0] != TAIL:
            raise TypeError("bad TAIL")
        # 拆包
        payload = pkg[2:]
        fmt = {8: "B", 16: "H", 32: "I", 64: "Q"}
        btsz = fmt[bit]
        size = struct.calcsize(btsz)
        # 检查格式
        if len(payload) % size != 0:
            raise TypeError("payload length not aligned to element size")
        # 计算数量
        num = len(payload) // size
        fmt = "<" + btsz * num
        # 提取数据
        return list(struct.unpack(fmt, payload))

    # 串口通信发送
    def send(self,data: List[int],bit: int = 16):
        # 构造包
        data=self._mkpkg(data,bit)
        # 发送
        self.uart.send(data)

    # 串口通信接收
    def recv(self,data: List[int],bit: int = 16):
        

