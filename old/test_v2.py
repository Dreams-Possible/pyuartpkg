import pyuart_v3 as uart
import time


# 检查串口
ports=uart.list_uart()
if(ports.list):
    # 指定默认串口为第一个
    defport=ports.list[0].device
else:
    raise RuntimeError("no uart device")

# 创建串口实例
ins= uart.UartIns()
# 初始化串口
ins.init(defport,115200)
# 发送测试数据
for i in range(5):
    # ins.sendauto_block("test")
    ins.send("test")
    time.sleep(1)


ins.deinit()