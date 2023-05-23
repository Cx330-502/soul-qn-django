
import base64

def encrypt(data):
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')


def decrypt(data):
    return base64.b64decode(data.encode('utf-8')).decode('utf-8')

if __name__ == '__main__':
    data0 = input("请输入要加密的内容：")
    data0 = str(data0)
    print("加密后的内容为：", encrypt(data0))
    print("解密后的内容为：", decrypt(encrypt(data0)))