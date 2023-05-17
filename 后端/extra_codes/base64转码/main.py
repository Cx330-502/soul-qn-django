import base64

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    file_path = "./files/1.txt"
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_name = f.name

    temp = base64.b64encode(file_content).decode('utf-8')
    print(temp)
    print(base64.b64decode(temp))
    print(base64.b64decode(temp).decode('utf-8'))
