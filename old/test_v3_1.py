
# 串口通信实例
class UartComuIns():

    # 实例初始化
    def __init__(self):
        # 标志位
        self.HEAD=ord('A')  #包头
        self.TAIL=ord('Z')  #包尾
        self.ESCAPE=ord('_')  #转义

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
        print(bytes([self.HEAD]) + bytes(escaped) + bytes([self.TAIL]))
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




def test_packet():
    com = UartComuIns()
    
    # 测试数据
    test_data = b"A_Z_hello_"  # 故意包含包头、包尾和转义符
    print("原始数据:", test_data)
    
    # 打包
    packed = com._mkpkg(test_data)
    print("打包结果:", packed)
    
    # 解包
    unpacked = com._dcpkg(packed)
    print("解包结果:", unpacked)
    
    # 验证是否一致
    assert unpacked == test_data, "解包结果与原始数据不一致"
    print("测试通过 ✅")

if __name__ == "__main__":
    test_packet()