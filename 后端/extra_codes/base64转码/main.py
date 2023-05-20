import base64
import os

# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    save_path = "./files.md"
    file_path = "./files/"
    with open(save_path, 'w') as save_file:
        save_file.write('文件列表\n')
    with open(save_path, 'a') as save_file:
        save_file.write('\n\n')
        for files in os.listdir(file_path):
            file_path1 = os.path.join(file_path, files)
            with open(file_path1, 'rb') as f:
                file_content = f.read()
                file_name = f.name
            save_file.write('### ' + file_name + '\n')
            temp = base64.b64encode(file_content).decode('utf-8')
            save_file.write('##### UTF8码：\n')
            save_file.write('```' + '\n')
            save_file.write(temp + '\n')
            save_file.write('```' + '\n')
            # save_file.write('##### 二进制码：\n')
            # save_file.write('```' + '\n')
            # save_file.write(str(file_content) + '\n')
            # save_file.write('```' + '\n')
            save_file.write('##### 解码：\n')
            save_file.write('```' + '\n')
            try:
                save_file.write(base64.b64decode(temp).decode('utf-8') + '\n')

            except:
                save_file.write('解码失败~\n')
            save_file.write('```' + '\n')
            save_file.write('------\n')
