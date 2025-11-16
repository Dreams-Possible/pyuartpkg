import struct
import time
import pyuart_v5 as uart

# 检查串口
ports = uart.list_uart()
if ports.list:
    defport = ports.list[0].device
else:
    raise RuntimeError("no uart device")

# 创建串口实例并初始化
uartins = uart.UartIns()
uartins.init(defport, 115200)

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

# -----------------------------
# 2️⃣ 发送 int 类型数据（16-bit）
int_data = [100, 200, 300, 400]
print("Send float bytes:", int_data)
data_bytes = struct.pack("<4H", *int_data)
comuins.send(data_bytes)
time.sleep(0.1)

received = comuins.recv()
if received:
    print("Received int bytes:", received)
    received_ints = struct.unpack("<4H", received)
    print("Decoded ints:", received_ints)
else:
    print("No int data received")

# -----------------------------
# 3️⃣ 发送混合数据（int + float）


mix_data = [100, 1.23, 200, 4.56]
print("Send float bytes:", mix_data)
data_bytes = struct.pack("<HfHf", *mix_data)
comuins.send(data_bytes)
time.sleep(0.1)

received = comuins.recv()
if received:
    print("Received mixed bytes:", received)
    decoded_mixed = struct.unpack("<HfHf", received)
    print("Decoded mixed data:", decoded_mixed)
else:
    print("No mixed data received")

# -----------------------------
# 反初始化串口
uartins.deinit()
