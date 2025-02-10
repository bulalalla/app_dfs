from common.command import *
from auto_control.controlor import *
import argparse
import re


class TestApk:

    def __init__(self, apk_path: str, pcapfile: str, sslkeylog: str):
        self.apk_path = apk_path
        self.pcapfile = pcapfile
        self.sslkeylog = sslkeylog

    def get_test_message(self):
        """
            根据apk获取测试前所需要的所有信息，包括apk的包名，启动activity名，以及app的uid等
        """
        try:
            # 构建 aapt 命令
            command = ["aapt2", "dump", "badging", self.apk_path]
            # 执行命令，捕获标准输出和标准错误，使用文本模式，并等待命令执行完成
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            aapt_output = result.stdout

            # 使用正则表达式提取 package 信息
            package_pattern = re.search(r"package: name='([^']+)'", aapt_output)
            package_name = package_pattern.group(1) if package_pattern else None

            # 使用正则表达式提取 launchable-activity 信息
            activity_pattern = re.search(r"launchable-activity: name='([^']+)'", aapt_output)
            activity_name = activity_pattern.group(1) if activity_pattern else None

            self.package_name = package_name
            self.activity_name = activity_name
            # 处理 pcapfile、sslkeylog 文件名
            self.pcapfile = self.pcapfile.replace("<package_name>", self.package_name)
            self.sslkeylog = self.sslkeylog.replace("<package_name>", self.package_name)

        except FileNotFoundError:
            print("错误：未找到 'aapt' 可执行文件，请确保 aapt 已正确安装并配置到系统环境变量中。")
        except subprocess.CalledProcessError as e:
            print(f"执行命令时出错：{e.stderr}")
        except IndexError:
            print("提取信息时出错，可能输出格式不符合预期。")

        try:
            # 构建 adb 命令
            command = f'adb shell "dumpsys package {self.package_name} | grep userid -i"'
            # 执行命令并捕获输出
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            output = result.stdout

            # 使用正则表达式提取 UID
            pattern = r"userId=(\d+)"
            match = re.search(pattern, output)
            if match:
                self.uid = match.group(1)
            else:
                print("未找到 UID 信息。")
                self.uid = None
        except subprocess.CalledProcessError as e:
            print(f"uid执行命令时出错: {e.stderr}")
            self.uid = None


def init_param():
    parser = argparse.ArgumentParser(prog="APPs AUTO CONTOL",
                                     description="本工具为APP自动测试工具，它会连接本地的MuMu模拟器默认127.0.0.1:7555端口，安装指定的APP，并自动产生尽可能多和不同的点击行为",
                                     add_help=True)
    parser.add_argument("-a", "--apk", help="apk, 待测试APP安装包的位置", required=False, type=str)
    parser.add_argument("--apkdir", help="当进行多个APP测试时，指定apk存放的文件夹", required=False, type=str)
    parser.add_argument("-p", "--pcapfile", help="apk产生的流量存储路径，默认值<package_name>.pcap", required=False, type=str)
    parser.add_argument("-k", "--sslkeylog", help="sslkeylog文件路径，默认值<package_name>.keylog", required=False, type=str)
    parser.add_argument("--pcapdir", help="进行多个APP测量时，产生的pcap文件的存储路径，默认值./results/pcap/", required=False, type=str)
    parser.add_argument("--keydir", help="进行多个APP测量时，产生的sslkeylog文件的存储路径，默认值./results/sslkeylog/", required=False, type=str)
    parser.add_argument("-t", "--timeout", help="APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成，默认值 300 秒", default=5 * 60, required=False, type=int)
    parser.add_argument("--round", help="APP测试的轮次，打开关闭APP多少次，每次代表遍历一遍完成，默认值 1", default=1, required=False, type=int)
    parser.add_argument("--depth", help="APP测试测试时的遍历深度", default=5, required=False, type=int)
    parser.add_argument("-d", "--device", help="device, 模拟器adb服务的运行端口，<ip_addr>:<port>，默认值127.0.0.1:7555", required=False, type=str)
    parser.add_argument("-s", "--script", help="中间人的处理脚本路径，默认值值E:\\work\\app_dfs\\mitmproxy\\mitmproxy_script.py", required=False, type=str)

    args = parser.parse_args()

    # 检查传参
    if args.apk is None and args.apkdir is None:
        print("ParamError: at least apk or apkdir is required!")
        parser.print_help()
        exit(-1)
    elif args.apk is not None and args.apkdir is not None:
        print("ParamError: apk and apkdir cannot be used at the same time!")
        parser.print_help()
        exit(-1)
    elif args.apk is not None:
        if not os.path.exists(args.apk):
            print(f"ParamError: {args.apk} is not exist!")
            exit(-1)
    elif args.apkdir is not None:
        if not os.path.exists(args.apkdir):
            print(f"ParamError: {args.apkdir} is not exist!")
            exit(-1)

    if args.pcapdir is not None and not os.exists(args.pcapdir):
        print(f"ParamError: {args.pcapdir} is not exist!")
        exit(-1)
    
    if args.keydir is not None and not os.exists(args.keydir):
        print(f"ParamError: {args.keydir} is not exist!")
        exit(-1)
    
    return {
        "apk_path": args.apk,
        "apkdir": args.apkdir,
        "pcapfile": args.pcapfile if args.pcapfile else "<package_name>.pcap",
        "sslkeylog": args.sslkeylog if args.sslkeylog else "<package_name>.keylog",
        "pcapdir": args.pcapdir if args.pcapdir else "./results/pcap/",
        "keydir": args.keydir if args.keydir else "./results/sslkeylog/",
        "timeout": args.timeout,
        "test_round": args.round,
        "dfs_depth": args.depth,
        "device": '127.0.0.1:7555' if not args.device else args.device,
        "mitm_script": "E:\\work\\app_dfs\\mitmproxy\\mitmproxy_script.py" if not args.script else args.script,
    }


def run_auto_test():
    # adb连接模拟器 & adb以root方式运行

    # 创建APP自动控制器
    controler = Controler(Operator=MumuOperator)
    controler.max_timeout = param["timeout"]
    controler.max_loop = param["test_round"]
    controler.max_depth = param["dfs_depth"]
    controler.app_package_name = None
    controler.app_activity_name = None
    sleep(1)
    # 依次对APP测量
    for test_apk in test_apk_list:
        # 1. 安装 apk
        if not adb_install_apk(test_apk.apk_path):
            print(f"{test_apk.apk_path} install failed!")
            continue
        # 2. 获取 apk 的测试所需的信息
        test_apk.get_test_message()
        # 将包名传递给中间人代理
        with open('E:\\work\\app_dfs\\mitmproxy\\currapp.txt', 'w') as file:
            file.write(test_apk.package_name)
        # 3. 运行中间人代理 & 开启抓包程序
        tcpdump_process = start_tcpdump(test_apk.package_name)
        mitm_process = start_mitmproxy(param["mitm_script"])
        # 4. 运行app自动测试脚本
        controler.app_package_name = test_apk.package_name
        controler.app_activity_name = test_apk.activity_name
        controler.run()

        # 5. 关闭中间人代理 & 抓包程序
        stop_tcpdump(tcpdump_process)
        stop_mitmproxy(mitm_process)
        # 6. 移动测试结果到指定目录
        move_results(src=f'/data/local/tmp/{test_apk.package_name}.pcap', dst=test_apk.pcapfile)
        copy_sslkeylog(dst=test_apk.sslkeylog)

        # 7. 卸载APP，恢复手机默认状态
        controler.operator.app_uninstall(test_apk.package_name)


if __name__ == '__main__':
    # 变量声明
    test_apk_list: list[TestApk] = []

    # 参数获取
    param = init_param()
    if param["apk_path"] is not None:
        test_apk_list.append(TestApk(param["apk_path"], param["pcapfile"], param["sslkeylog"]))
    elif param["apkdir"] is not None:
        test_apk_list.extend([TestApk(os.path.join(param["apkdir"], apk),
                                      os.path.join(param["pcapdir"],"<package_name>.pcap"),
                                      os.path.join(param["keydir"],"<package_name>.keylog"))
                              for apk in os.listdir(param["apkdir"]) if apk.endswith(".apk") or apk.endswith(".xapk")])
    else:
        print("不可能的")
        exit(-1)
    
    run_auto_test()
