from command import *
from auto_control.controlor import *

if __name__ == '__main__':
    task_list = {
        'connect_device': ['adb', 'connect', '127.0.0.1:7555'],
        'get_root': ['adb', 'root'],
        'capture_traffic': ['adb', 'shell', 'tcpdump', '-i any', '-w /data/local/tmp/{filename}.pcap'],
        'mitm_proxy': ['mitmdump', '-s xx.py', '--upstream=127.0.0.1:7890', '-p 18080'],
    }
    # 创建后台任务并执行
    bkt = BackgroundTask(tasks=task_list)
    # 检查
    sleep(1) # 等待非耗时任务执行完毕
    # 姑且认为返回0代表正常执行完毕
    if not(bkt.returncode("connect_device") == 0 and bkt.returncode("get_root") == 0):
        raise "adb找不到设备"
    else:
        print("adb连接成功...")
    if not(bkt.returncode("capture_traffic") == None):
        raise "后台未启动抓包"
    else:
        print("Android抓包中...")
    if not(bkt.returncode("mitm_proxy") == None):
        raise "后台未启中间人代理"
    else:
        print("中间人代理进行中...")

    # 创建driver，确定要操纵的app
    controler = Controler(Operator=MumuOperator, 
                          app_package_name="com.android.settings",
                          app_activity_name="com.android.settings.Settings")
    # 开始执行app_dfs
    controler.run()

    # 创建收尾的后台任务并执行
    bkt.add(task_id="pull_pcap", task_cmd=["adb", "pull", "/data/local/tmp/{filename}.pcap", "./resutls/"])
    # 杀死所有进程
    sleep(1)    # 等待文件传输完成
    bkt.stop_all()