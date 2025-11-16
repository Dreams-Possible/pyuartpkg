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

# 创建串口1实例并初始化
uartins1 = uart.UartIns()
if not uartins1.init(ports.list[0].device, 115200):
    raise RuntimeError("can not init uart")

# 创建串口1通信实例并绑定
comuins1 = uart.UartComuIns()
comuins1.init(uartins1)

time.sleep(0.1)  # 等待串口稳定

while True:
    # -----------------------------
    # 1️⃣ 发送 float 类型数据（模拟一次传感器 4 个 float）
    float_data = [1.23, 4.56, 7.89, 0.12]
    print("Send float bytes:", float_data)
    data_bytes = struct.pack("<4f", *float_data)
    comuins1.send(data_bytes)
    time.sleep(0.001)