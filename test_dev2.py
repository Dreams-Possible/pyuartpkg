import struct
import time
import pyuart_v7 as uart

# 检查串口
ports = uart.list_uart()
# 绑定默认串口
if ports.list:
    defport = ports.list[0].device
else:
    raise RuntimeError("no uart device")

# 创建串口2实例并初始化
uartins2 = uart.UartIns()
if not uartins2.init(ports.list[1].device, 115200):
    raise RuntimeError("can not init uart")

# 创建串口2通信实例并绑定
comuins2 = uart.UartComuIns()
comuins2.init(uartins2)

time.sleep(0.1)  # 等待串口稳定

while True:
    # 接收可能包含多帧
    received_pkgs = comuins2.recv()
    
    if received_pkgs:
        for pkg in received_pkgs:
            # print("Received raw bytes:", pkg)
            # 假设每帧都是 4 个 float
            try:
                decoded_floats = struct.unpack("<4f", pkg)
                print("Decoded floats:", decoded_floats)
            except:
                print("Error decoding this frame")
    # else:
        # 没有数据
        # time.sleep(0.01)
