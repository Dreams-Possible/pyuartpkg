import struct
import time
import pyuart_v6 as uart

# 检查串口
ports = uart.list_uart()
if ports.list:
    defport = ports.list[0].device
else:
    raise RuntimeError("no uart device")

# 创建串口实例并初始化
uartins = uart.UartIns()
if not uartins.init(defport, 115200):
    raise RuntimeError("can not init uart")

# 创建串口通信实例并绑定
comuins = uart.UartComuIns()
comuins.init(uartins)

time.sleep(0.1)  # 等待串口稳定

# -----------------------------
# 1️⃣ 发送 float 类型数据（模拟一次传感器 4 个 float）
float_data = [1.23, 4.56, 7.89, 0.12]
print("Send float bytes:", float_data)
data_bytes = struct.pack("<4f", *float_data)
comuins.send(data_bytes)
time.sleep(0.1)

received = comuins.recv()
if received:
    print("Received float bytes:", received)
    received_floats = struct.unpack("<4f", received)
    print("Decoded floats:", received_floats)
else:
    print("No float data received")
