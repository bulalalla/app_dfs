from command import *
from controlor import *
import argparse
import re


def run_background_task():
    # task = tuple(cmd: list[], )
    tasks_desc = {
        'capture_traffic': (['adb', 'shell', 'tcpdump', '-i any', '-w /data/local/tmp/{filename}.pcap'], 1),
        'mitm_proxy': (['mitmdump', '-s xx.py', '--upstream=127.0.0.1:7890', '-p 18080'], 1),
    }
    tasks = []
    for k, v in tasks_desc.items():
        tasks.append(Task(task_id=k, task_cmd=v[0], slow=v[1]))
    tm = TaskManager(tasks=tasks)
    tm.run_all()
    # 找到瞬间能执行完毕的task 只有它们的执行结果正确，才能继续向下执行
    quick_tasks = tm.find_slow_task(slow=False)
    tm.recv_all(tasks=quick_tasks)
    for quick_task in quick_tasks:
        if quick_task.status in ["RUNNING", "ERROR"]:
            raise f"Task with id: {quick_task.id} is running or return error, we can't continue until it be successfully done."
    # 找到需要在后台一直运行的task 只有它们一直处于running状态，才能继续向下执行 
    slow_tasks = tm.find_slow_task(slow=True)
    tm.recv_all(tasks=slow_tasks)  # recv会尝试把process已经停止的task recv
    for slow_task in slow_tasks:
        if slow_task.status != "RUNNING":
            raise f"Task with id: {quick_task.id} is not running, we need it running to capture data."

    return tm


def init():
    parser = argparse.ArgumentParser(prog="APP AUTO CONTOL",
                                     usage="",
                                     description="本工具为APP自动测试工具，它会连接本地的模拟器默认127.0.0.1:7555端口，安装指定的APP，并自动产生尽可能多和不同的点击行为",
                                     add_help=True)
    parser.add_argument("--apk", help="apk, 待测试APP安装包的位置", default="E:/apks/com.weaver.app.prod.apk")
    parser.add_argument("--device", help="device, 模拟器adb服务的运行端口，<ip_addr>:<port>", default="127.0.0.1:7555")
    parser.add_argument("--round", help="APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成", default=10)
    parser.add_argument("--depth", help="APP测试测试时的遍历深度", default="10")
    parser.add_argument("--script", help="中间人的脚本路径", default="xx.py")
    parser.add_argument("--pcapfile", help="测试过程中，APP产生的流量的路径", default="<app_package_name>.pcap")

    res = dict()
    param = parser.parse_args()

    app_abs_path = param.apk
    device = param.device
    for_round = param.round
    dfs_depth = param.depth
    mitm_script_abs = param.script
    pcap_filename = param.pcapfile

    # 获取package名和activity名
    # Step 1: 执行 aapt 命令并使用 Select-String 模拟筛选行
    aapt_process = subprocess.Popen(f'aapt dump badging "{app_abs_path}"', stdout=subprocess.PIPE, shell=True)
    aapt_output = aapt_process.communicate()[0].decode()

    # 筛选出 package 和 activity 信息
    package_pattern = re.search(r"package: name='([^']+)'", aapt_output)
    activity_pattern = re.search(r"launchable-activity: name='([^']+)'", aapt_output)

    if package_pattern and activity_pattern:
        app_package_name = package_pattern.group(1)
        app_activity_name = activity_pattern.group(1)
    else:
        raise "init error, not find app_package_name or app_activity_name"

    # 连接emulator 并 获取root
    connect_proccess = subprocess.Popen(f"adb connect {device}", stdout=subprocess.PIPE, shell=True)
    root_proccess = subprocess.Popen(f"adb root", stdout=subprocess.PIPE, shell=True)
    time.sleep(2)
    connect_output = connect_proccess.communicate()[0].decode()
    # TODO 暂时认为不会连接失败
    if "连接失败的判断":
        pass

    # 安装app
    install_process = subprocess.Popen(f'adb install "{app_abs_path}"', stdout=subprocess.PIPE, shell=True)
    time.sleep(2)
    install_output = install_process.communicate()[0].decode()
    if 'unsuccessful' in install_output or 'Unsuccessful' in install_output:
        raise f"init error, can't install {app_abs_path} to emulator, maybe apk's arch not match with emulator's arch"

    res.update({
        "app_abs_path": app_abs_path,
        "device": device,
        "for_round": for_round,
        "dfs_depth": dfs_depth,
        "mitm_script_abs": mitm_script_abs,
        "pcap_filename": pcap_filename,
        "app_package_name": app_package_name,
        "app_activity_name": app_activity_name,
        "uid": 10100    # app的uid，这显然是一个假的数字
    })

    return res


if __name__ == '__main__':
    # 接收参数 并 计算 app的包名和启动activity
    parameters = init()
    
    # app自动测试前需要执行的任务
    task_manager = run_background_task()

    # 创建控制器
    controler = Controler(Operator=MumuOperator,
                          app_activity_name=parameters['app_activity_name'],
                          app_package_name=parameters['app_package_name'])
                          
    # 开始执行app_dfs
    controler.run()

    # 创建收尾的后台任务并执行
    task_manager.add_and_run(Task(task_id="pull_pcap", task_cmd=["adb", "pull", "/data/local/tmp/{filename}.pcap", "./resutls/"], slow=False))
    # 杀死所有进程
    task_manager.stop_all()
    

