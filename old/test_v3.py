import pyuart_v3_1 as uart
import time


# 检查串口
ports=uart.list_uart()
if(ports.list):
    # 指定默认串口为第一个
    defport=ports.list[0].device
else:
    raise RuntimeError("no uart device")

# 创建串口实例
uartins= uart.UartIns()
# 初始化串口
uartins.init(defport,115200)

# 创建串口通信实例
comuins= uart.UartComuIns()
# 初始化串口
comuins.init(uartins)


# 发送测试数据
for i in range(5):
    comuins.send("te_st")
    time.sleep(1)

# 反初始化串口
uartins.deinit()