import struct
from typing import List

class UartComuIns:

    ESCAPE = 0x7D       # 转义符
    HEAD = 0xAA         # 包头（简化为单字节）
    TAIL = 0x55         # 包尾（简化为单字节）

    # 打包函数：自动加包头/包尾并转义
    def _mkpkg(self, data: List[int]) -> bytes:
        raw = bytes(data)

        # 转义：出现特殊字节时替换
        escaped = bytearray()
        for b in raw:
            if b == self.HEAD:
                escaped.extend([self.ESCAPE, 0x5A])  # 转义 0xAA -> [0x7D, 0x5A]
            elif b == self.ESCAPE:
                escaped.extend([self.ESCAPE, 0x5D])  # 转义 0x7D -> [0x7D, 0x5D]
            else:
                escaped.append(b)

        # 最终包结构：HEAD + 数据 + TAIL
        return bytes([self.HEAD]) + bytes(escaped) + bytes([self.TAIL])


    # 解包函数：去包头包尾 + 反转义
    def _dcpkg(self, pkg: bytes) -> List[int]:
        if pkg[0] != self.HEAD or pkg[-1] != self.TAIL:
            raise ValueError("bad packet header or tail")

        payload = pkg[1:-1]
        decoded = bytearray()

        i = 0
        while i < len(payload):
            b = payload[i]
            if b == self.ESCAPE:
                # 说明这是转义序列
                i += 1
                if i >= len(payload):
                    raise ValueError("incomplete escape sequence")

                next_b = payload[i]
                if next_b == 0x5A:
                    decoded.append(self.HEAD)
                elif next_b == 0x5D:
                    decoded.append(self.ESCAPE)
                else:
                    raise ValueError("invalid escape sequence")
            else:
                decoded.append(b)
            i += 1

        return list(decoded)
