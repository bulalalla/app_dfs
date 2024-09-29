from command import *
from controlor import *
import argparse
import re


def init(tm: TaskManager):
    parser = argparse.ArgumentParser(prog="APP AUTO CONTOL",
                                     usage="",
                                     description="本工具为APP自动测试工具，它会连接本地的模拟器默认127.0.0.1:7555端口，安装指定的APP，并自动产生尽可能多和不同的点击行为",
                                     add_help=True)
    parser.add_argument("--apk", help="apk, 待测试APP安装包的位置", default="E:/apks/Washington_Post_6.42.1.apk")
    parser.add_argument("--device", help="device, 模拟器adb服务的运行端口，<ip_addr>:<port>", default="127.0.0.1:7555")
    parser.add_argument("--round", help="APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成", default=5)
    parser.add_argument("--depth", help="APP测试测试时的遍历深度", default=2)
    parser.add_argument("--script", help="中间人的脚本路径", default="E:\\work\\app_auto_test\\mitmproxy\\mitmproxy_script.py")
    parser.add_argument("--pcapfile", help="测试过程中，APP产生的流量的路径", default="default.pcap")

    res = dict()
    param = parser.parse_args()

    app_abs_path = param.apk
    device = param.device
    for_round = int(param.round)
    dfs_depth = int(param.depth)
    mitm_script_abs = param.script
    pcap_filename = param.pcapfile

    # 连接Emulator并获取root
    tm.add_and_run(Task(task_id="adb_connect", task_cmd=["adb", "connect", device], slow=False))
    tm.add_and_run(Task(task_id="adb_root", task_cmd=["adb", "root"], slow=False))
    tm.recv_all()
    # 检验是否会连接失败，失败则不再继续
    task_connect = tm.find_task(task_id="adb_connect")
    task_root = tm.find_task(task_id="adb_root")
    if task_connect.dealwith_adb() == -1 or task_root.dealwith_adb() == -1:
        error_str = f"adb error: {task_connect.exe_result_str}; {task_root.exe_result_str}"
        raise error_str

    # 获取package名和activity名
    # Step 1: 执行 aapt 命令并使用 Select-String 模拟筛选行
    tm.add_and_run(Task(task_id="aapt_dump", task_cmd=["aapt", "dump", "badging", app_abs_path], slow=False))
    task_aapt = tm.find_task(task_id="aapt_dump")
    task_aapt.recv()
    if task_aapt.dealwith_aapt() == -1:
        raise "aapt获取package name和activity name失败"

    # 安装app
    tm.add_and_run(Task(task_id="adb_install", task_cmd=["adb", "install", app_abs_path], slow=False))
    task_install = tm.find_task(task_id="adb_install")
    task_install.recv()
    if task_install.dealwith_adb() == -1:
        error_str = f"adb error: {task_install.exe_result_str}"
        raise error_str
    else:
        # 将currapp名字写入 .\mitmproxy\currapp.txt文件中，因为中间人脚本需要用到
        with open("E:\\work\\app_auto_test\\mitmproxy\\currapp.txt", 'w', encoding='utf-8') as file:
            file.write(task_aapt.exe_result.get("app_package_name"))

    res.update({
        "app_abs_path": app_abs_path,
        "device": device,
        "for_round": for_round,
        "dfs_depth": dfs_depth,
        "mitm_script_abs": mitm_script_abs,
        "pcap_filename": pcap_filename if pcap_filename != "default.pcap" else task_aapt.exe_result.get("app_package_name") + ".pcap",
        "app_package_name": task_aapt.exe_result.get("app_package_name"),
        "app_activity_name": task_aapt.exe_result.get("app_activity_name"),
        "uid": 10100    # app的uid，这显然是一个假的数字
    })

    return res


def run_background_task(tm: TaskManager):
    """
        运行后台进程
        return returncode, 0成功 -1代表第一个任务失败，-2代表第二个失败，依次类推
    """
    tasks = [
        Task(task_id="tcpdump_capture_traffic",
             task_cmd=['adb', 'shell', 'tcpdump', f"-w /data/local/tmp/{parameters['pcap_filename']}", '-i any not port 5555 and not port 7555 and not port 5553 and not port 5554 and not port 5353'],
             slow=True),
        Task(task_id="mitm_proxy", task_cmd=['mitmdump', '-s', parameters['mitm_script_abs'], '--upstream=127.0.0.1:7890', '-p 18080'], slow=True)
    ]
    
    tm.tasks_list.extend(tasks)
    tm.run_all()
    # 找到需要在后台一直运行的task 只有它们一直处于running状态，才能继续向下执行 
    slow_tasks = tm.find_slow_task(slow=True)
    flag = -1
    for slow_task in slow_tasks:
        # 判断子进程是否终止
        if slow_task.process.poll():
            print(f"Warning: Task with id: {slow_task.id} is not running, may you need run it. Please check is the tool installed and cmd is correct.")
            return flag
        flag -= 1
    return 0 if flag == -(len(tasks) + 1) else flag


if __name__ == '__main__':
    task_manager = TaskManager(None)
    # 1. 接收参数
    # 2. 连接模拟器
    # 3. 获取app的包名和启动activity名，安装app到模拟器
    # 若init失败，则不应该继续执行，!需要抛出异常!
    try:
        parameters = init(tm=task_manager)
        for k,v in parameters.items():
            print(f"{k}: {v}")
    except Exception as e:
        print(f"init error! {e}")
        exit(-1)
    
    try:
        # 打开自动测试APP时的后台任务：抓包、中间人代理等
        # 若此步骤失败，则不影响APP自动测试，可以根据需要继续向下执行；!不应该抛出异常!
        returncode = run_background_task(tm=task_manager)
        if returncode == 0 or returncode != 0:
            # 当前设置为，无论如何，都可以继续执行
            pass
        
        # 创建控制器
        controler = Controler(Operator=MumuOperator,
                            app_activity_name=parameters['app_activity_name'],
                            app_package_name=parameters['app_package_name'],
                            max_depth=parameters["dfs_depth"],
                            max_loop=parameters["for_round"])
                            
        # 开始执行app_dfs
        controler.run()
        # pass
        # 停止抓包
        task_pcap = task_manager.find_task(task_id="tcpdump_capture_traffic")
        task_pcap.stop()
        # 创建收尾的后台任务并执行
        task_manager.add_and_run(Task(task_id="pull_pcap", task_cmd=["adb", "pull", f"/data/local/tmp/{parameters['pcap_filename']}.pcap", "./results/traffic/"], slow=False))
        task_manager.add_and_run(Task(task_id="uninstall", task_cmd=["adb", "uninstall", parameters["app_package_name"]], slow=False))
    except:
        pass
    finally:
        print("clear tasks...")
        # 正常结束抓包进程
        task_manager.stop_all()
        print("clear over")

