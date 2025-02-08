import subprocess
import os
import shutil

def adb_connect_device(device):
    try:
        # 构建要执行的 ADB 命令
        command = ['adb', 'connect', device]
        # 执行命令并等待其完成
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # 检查命令输出中是否包含连接成功的信息
        output = result.stdout.lower()
        if 'connected to' in output:
            return True
        else:
            print("Error: Failed to connect to device")
            exit(-1)
    except subprocess.CalledProcessError as e:
        # 若命令执行出错，打印错误信息并返回 False
        print(f"Error: {e.stderr}")
        exit(-1)


def adb_install_apk(apk_path):
    try:
        # 构建 adb install 命令
        command = ['adb', 'install', apk_path]
        # 执行命令，捕获标准输出和标准错误，使用文本模式，并检查返回码
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # 获取命令执行的标准输出
        output = result.stdout.lower()
        # 检查输出中是否包含安装成功的标志信息
        if 'success' in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        # 若命令执行过程中出现错误，打印错误信息
        print(f"Error: {e.stderr}")
        return False


def start_tcpdump(filename):
    try:
        # 构建 tcpdump 命令
        command = [
            'adb', 'shell', 'tcpdump',
            f"-w /data/local/tmp/{filename}.pcap",
            '-i any',
            'not port 5555 and not port 7555 and not port 5553 and not port 5554 and not port 5353'
        ]
        # 启动 tcpdump 进程，不阻塞主程序
        tcpdump_process = subprocess.Popen(command)
        print("tcpdump 命令已启动。")
        return tcpdump_process
    except Exception as e:
        print(f"启动 tcpdump 时出错: {e}")
        return None

def stop_tcpdump(tcpdump_process):
    if tcpdump_process:
        try:
            # 尝试终止 tcpdump 进程
            tcpdump_process.terminate()
            # 等待进程结束
            tcpdump_process.wait()
            print("tcpdump 命令已停止。")
        except Exception as e:
            print(f"停止 tcpdump 时出错: {e}")
        finally:
            tcpdump_process = None
    else:
        print("tcpdump 进程未启动。")


def start_mitmproxy(script):
    try:
        # 构建 mitmproxy 命令
        command = [
            'mitmdump', 
            '-s', script, 
            '-p', 18080,
            '--upstream=127.0.0.1:7890', 
        ]
        # 启动 mitmproxy 进程，不阻塞主程序
        mitmproxy_process = subprocess.Popen(command)
        print("mitmproxy 命令已启动。")
        return mitmproxy_process
    except Exception as e:
        print(f"启动 mitmproxy 时出错: {e}")
        return None

def stop_mitmproxy(mitmproxy_process):
    if mitmproxy_process:
        try:
            # 尝试终止 mitmproxy 进程
            mitmproxy_process.terminate()
            # 等待进程结束
            mitmproxy_process.wait()
            print("mitmproxy 命令已停止。")
        except Exception as e:
            print(f"停止 mitmproxy 时出错: {e}")
        finally:
            mitmproxy_process = None
    else:
        print("mitmproxy 进程未启动。")

        
def move_results(src, dst):
    try:
        # 构建 adb pull 命令
        command = ['adb', 'pull', src, dst]
        # 执行命令
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # 检查命令输出，若没有错误信息则认为执行成功
        if not result.stderr:
            return True
        else:
            print(f"执行 adb pull 时出错: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"执行 adb pull 时出错: {e.stderr}")
        return False
    

def copy_sslkeylog(dst):
    # 获取 SSLKEYLOG 环境变量指定的文件路径
    sslkeylog_path = os.getenv('SSLKEYLOG')
    if not sslkeylog_path:
        print("未设置 SSLKEYLOG 环境变量。")
        return False

    try:
        # 检查 SSLKEYLOG 文件是否存在
        if os.path.exists(sslkeylog_path):
            # 复制文件到目标路径
            shutil.copy2(sslkeylog_path, dst)
            # 清空 SSLKEYLOG 文件
            with open(sslkeylog_path, 'w') as f:
                f.write('')
            return True
        else:
            print(f"SSLKEYLOG 指定的文件 {sslkeylog_path} 不存在。")
            return False
    except Exception as e:
        print(f"复制或清空 SSLKEYLOG 文件时出错: {e}")
        return False