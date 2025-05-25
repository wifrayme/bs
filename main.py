import subprocess
import threading
import time
import os

def start_msf():
    # 初始化 msfdb
    subprocess.run(["msfdb", "init"])
    # 启动 msfconsole，并自动输入命令
    msfconsole = subprocess.Popen(
        ["msfconsole", "-q"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True  # 兼容 Python 3.6
    )
    # 给 msfconsole 输入命令
    msgrpc_cmd = "load msgrpc ServerHost=192.168.111.141 ServerPort=55553 User=test Pass=test1234\n"
    time.sleep(10)  # 等待 msfconsole 启动
    msfconsole.stdin.write(msgrpc_cmd)
    msfconsole.stdin.flush()
    # 持续读取 msfconsole 的输出
    while True:
        output = msfconsole.stdout.readline()
        if output == '' and msfconsole.poll() is not None:
            break
        if output:
            print("[msfconsole]", output.strip())

def start_web():
    # 启动 web 界面，注意文件名和你的实际文件一致
    os.system("python3 mlsec_webui.py")

if __name__ == "__main__":
    t1 = threading.Thread(target=start_msf)
    t1.daemon = True
    t1.start()
    t2 = threading.Thread(target=start_web)
    t2.daemon = False
    t2.start()
    t2.join()