import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import time
import re
from typing import Optional, Union
import pandas as pd
from tqdm import tqdm

from common.base_operation import *
from common.datastruct import *


class GoogleSpider:

    def __init__(self, operator: MumuOperator):
        self.operator = operator
        self.play_package = "com.android.vending"
        self.play_activity = "com.google.android.finsky.activities.MainActivity"
        self.rank_target = List[Tuple[str, str]]
    
    def network_check(self) -> bool:
        """
            检查是否能够访问外网
        """
        shell_resp = self.operator.device.shell("ping -c 4 www.google.com")
        print(f"exit code: {shell_resp.exit_code}\n output:\n{shell_resp.output}", end='')
        return "0 received" not in shell_resp.output

    def play_login_check(self) -> bool:
        """
            检查是否已经具有登录账号
        """
        operator.start_app(package_name=self.play_activity, start_activity=self.play_activity)
        login_button = wait_until(self.operator,
                                xpath="./android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[2]/android.widget.Button[4]",
                                timeout=10,
                                retry=3)
        if login_button:
            return False
        else:
            return True
    
    def init_spider(self) -> bool:
        # 检查网络环境
        if not self.network_check():
            print("当前网络环境不支持访问Google Play")
            return False
        # 重启/启动APP
        self.operator.start_app(self.play_package, self.play_activity)
        # 检查是否已经登录
        if not self.play_login_check():
            print("未登录Google账号，无法继续")
            return False
        return True

    def set_rank_target(self, target: List[Tuple[str, str]]):
        """
            设置爬取目标，格式：[(设备类型, APP类型)]
        """
        self.target_device_type = target

    def app_info(self, app_element: UIBlock, ) -> Dict:
        """
            收集某个APP的信息
            param app_element: 代表rank页面一个APP的条目
        """
        # 0. item上的信息
        app_rank = app_element.find(path='.//android.widget.TextView[1]').attrib['text']
        app_icon = app_element.find(path='.//android.view.View[1]')
        app_desc = app_element.find(path='.//android.view.View[2]').attrib['content-desc'].split('\n')
        app_name = app_desc[0]
        # 有时这里会多出一条
        if re.search(r'\d', app_desc[-2]):
            app_categories = app_desc[1:-2]
            app_score = app_desc[-2]
        else:
            app_categories = app_desc[1:-3]
            app_score = app_desc[-3]

        # 1. 点击APPitem，进入对应页面
        self.operator.click(*app_element.center)
        time.sleep(0.5)
        # 等待加载
        app_screen = wait_until(self.operator, xpath=f'.//*[@text="{app_name}"]', timeout=10, retry=3)
        # 2. 收集信息
        back_button = app_screen.find(path='.//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[2]/android.view.View[1]')
        text_view = app_screen.findall(path=".//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.widget.TextView")
        view_view = app_screen.findall(path=".//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View")
        app_org = text_view[0].attrib['text']
        app_comment_count = view_view[1].attrib['content-desc']
        app_download_count = view_view[2].attrib['content-desc']
        app_user = view_view[-2].attrib['content-desc']
        install_button = view_view[-1]
        
        # 3. 返回结果
        res = {
            'Rank': int(app_rank),
            'Name': app_name,
            'Category': "·".join(app_categories),
            'Developer': app_org,
            'Score': app_score,
            'Commnet': app_comment_count,
            'Download': app_download_count,
            'User': app_user
        }
        print("=" * 20)
        for k, v in res.items():
            print(f"{k}: {v}")
        # 返回
        self.operator.click(*back_button.center)
        return res

    def rank_of(self, device_type, app_category, top_n=200) -> List[Dict]:
        """
            爬取指定设备类型、指定app类别前 top_n 个app
            param device_type: 设备类型
            param app_category: app的类别
            param top_n: 最多爬取前多少个 目前Google Play Store针对每个类别似乎最多只展示200个
        """
        # 按照固定的步骤进入到应用排名页面
        op_step = [
            ('application button', './/*[@text="应用"]'),
            ('rank and hot', './/*[@text="热门排行榜"]'),
            # ('category button', './/android.widget.HorizontalScrollView/android.view.View[2]/android.view.View[2]')
        ]
        for desc, xpath in op_step:
            button = wait_until(operator=self.operator, xpath=xpath, timeout=10, retry=3)
            if button is not None:
                self.operator.click(*button.center)
            else:
                raise LookupError(f"{desc} not found")
        
        # # 找到对应的类别
        # u2 获取不到悬浮的内容，不能这么写了
        # window = ('category select', './/android.support.v7.widget.RecyclerView')
        # window_ele = wait_for(operator=self.operator, element_desc=window[1], timeout=10, retry=3)
        # print(etree.tostring(window_ele.getroot(), pretty_print=True, encoding='UTF-8').decode('UTF-8'))
        # if window_ele is not None:
        #     # TODO 假设一定能查找到，查找不到会死循环
        #     while True:
        #         category_button = window_ele.find(f'.//*[@content-desc="{app_category}"]')
        #         if category_button is not None:
        #             self.operator.click(*category_button.center)
        #             break
        #         else:
        #             # 滑动查找
        #             xlen = abs(window_ele.bounds[0][0] - window_ele.bounds[1][0])
        #             ylen = abs(window_ele.bounds[0][1] - window_ele.bounds[1][1])
        #             center_x, center_y = window_ele.center[0], window_ele.center[1]
        #             self.operator.scroll(center_x, center_y, center_x, center_y-ylen//2)
        
        # 挨个点击app并爬取
        curr_rank = 1
        apps_info = []
        try:
            while True:
                screen = UIBlock(xml_str=self.operator.dump_hierarchy())
                # 获取每个APP条目
                apps = screen.findall(path='.//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[4]/android.view.View')
                flag = False
                for app_item in apps:
                    try:
                        # 获取rank
                        rank = int(app_item.find(".//android.widget.TextView[1]").attrib['text'])
                        if rank < curr_rank:
                            continue
                        flag = True
                        # 进入app页面内部爬取
                        apps_info.append(self.app_info(app_item))
                        curr_rank += 1
                        time.sleep(1)
                    except:
                        continue

                # 没有新的APP或爬取到达设定最大值
                if not flag or curr_rank > top_n:
                    break
                self.operator.scroll(*apps[-1].center, *apps[0].center)
        except Exception as e:
            raise e
        finally:
            # 存储已爬取到的信息
            df = pd.DataFrame(apps_info)
            with pd.ExcelWriter('./app_rank.xlsx', engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=f'{device_type}-{app_category}', index=False)
    
    def run_rank_spider(self):
        # 初始化
        if not self.init_spider():
            return 
        for device, app_category in self.rank_target:
            try:    # 出现错误就重新初始化，接着下一个继续跑
                self.rank_of(device, app_category)
            except:
                if not self.init_spider():
                    return
                
    def run_apk_spider(self, app_info: Dict, save_dir: str, filename=None) -> Union[bool, List[str]]:
        """
            获取某个app的apk文件
            param app_info: 一个app信息的字典 其中name字段的信息将被输入到Google Play Store进行搜索 然后下载第一个APP
            param save_dir: apk的存储目录
            param filename: apk的存储文件名 若不传入则默认以包名命名 推荐不传入此参数
            return: 成功返回文件路径 一个APP可能对应多个APK 失败返回False
        """
        def search(input_text) -> bool:
            """
                搜索栏中输入内容并搜索 进入第一个搜到的APP 返回此界面的APP元素
            """
            # 1. 点击搜索按钮，进入搜索页面
            screen = UIBlock(xml_str=self.operator.dump_hierarchy())
            search_button = screen.find('.//*[@text="搜索"]')
            if search_button:
                self.operator.click(*search_button.center)
            
            # 2. 输入并搜索
            screen = UIBlock(xml_str=self.operator.dump_hierarchy())
            search_texteara = screen.find('.//*[@text="搜索应用和游戏"]')
            if not search_texteara:
                print("Didn't found the search box")
                return False
            self.operator.input(input_text, *search_texteara.center)
            self.operator.press_key(KEYCODE_ENTER)
            time.sleep(2)   # 等待搜索结果
            return True

        def get_packages_info(app_name) -> Optional[str]:
            """
                使用shell的 pm命令获取packages相关信息 里面包含安装包位置和包名
            """
            shell_resp = self.operator.shell(cmdargs=['pm', 'list', 'packages', '-3', '-f']) # -3 第三方APP -f 列举相关文件 即APK位置
            info = shell_resp.output
            if shell_resp.exit_code != 0:
                print(f"Can't get APK file of {app_name}, because the shell cmd run error")
                return None
            return info

        def find_new_apps(last_packages, new_packages) -> List[Tuple[str, str]]:
            """
                对比 app 安装前后使用 "pm list packages -f -3"指令获得的字符串 从而发现新安装APP的APK位置和包名
            """
            # 将字符串按行分割成集合
            lines1 = set(last_packages.splitlines())
            lines2 = set(new_packages.splitlines())
            # 找到 str2 比 str1 多的行
            extra_lines = lines2 - lines1
            # 提取路径和包名
            path_and_packages = []
            for line in extra_lines:
                # 提取路径和包名
                package_name = line.split("=")[-1]
                path = line[:-len(package_name)-1].removeprefix("package:")
                path_and_packages.append((path.strip(), package_name.strip()))
            # 返回
            return path_and_packages
        
        def wait_for_download(app_name):
            """
            等待下载APP直至完成
            """
            print(f"Waiting for {app_name} downloading...")
            # 初始化进度条
            pbar = tqdm(total=100, desc="Download Progress", unit="%")
            progress = 0
            # 循环检查进度
            while True:
                screen = UIBlock(xml_str=self.operator.dump_hierarchy())
                progress_elements = screen.xpath('.//*[contains(@content-desc, "%")]')
                open_button = screen.find('.//*[@text="打开"]')
                if progress_elements:
                    match = re.search(r'(\d+)%', progress_elements[-1].attrib['content-desc'])
                    if match:
                        progress = int(match.group(1))
                # 进度条显示可能错误，如果发现打开按钮，说明已经下载好了
                if open_button:
                    progress = 100
                # 更新进度条
                pbar.n = progress
                pbar.refresh()
                if progress >= 100:
                    break
            
            pbar.close()
            print(f"{app_name} download completed.")
            time.sleep(3)
            print("Waiting for install...")
            while True:
                screen = UIBlock(xml_str=self.operator.dump_hierarchy())
                installing = screen.findall('.//*[@content-desc="正在安装..."]')
                if not installing:
                    break
                time.sleep(1)
            print(f"{app_name} install completed.")

        def download_apk(app_name):
            """
            下载APP
            """
            # 1. 结果有多个，找到最佳匹配（第一个）
            screen = UIBlock(xml_str=self.operator.dump_hierarchy())
            matched_apps = screen.xpath(f'.//*[contains(@content-desc, "{app_name}")]')
            if not matched_apps:
                may_match = screen.find('.//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[1]/android.view.View[2]')
                if may_match:
                    matched_apps.append(may_match) 
                    print(f"Can't find the best match app of {app_name}, please please check the download result.")

            # 点击第一个
            if matched_apps:
                self.operator.click(*matched_apps[0].center)
                time.sleep(1)
            else:
                pass
    
            # 2. 点击安装
            install_buttons = None
            for i in range(5):
                screen = UIBlock(xml_str=self.operator.dump_hierarchy())
                right_view = screen.find('.//androidx.compose.ui.platform.ComposeView/android.view.View[1]/android.view.View[2]')
                
                # 考虑两种情况：1. 平板模式，左右分栏 2. 进入主页面，无左右分栏
                if right_view:
                    install_buttons = right_view.findall('.//*[@content-desc="安装"]')
                else:
                    install_buttons = screen.findall('.//*[@content-desc="安装"]')
                if install_buttons:
                    self.operator.click(*install_buttons[-1].center)
                    wait_for_download(app_name)
                    return True
            print(f"Can't find install button of {app_name}")
            return False
            
        # ==== Begin ====
        # 这里默认已经打开了 Google Play Store，且到达了首页，网络正常，登录状态正常
        if app_info.get('name') is None:
            print("Please input the app name")
            return False
        # 0. 记录当前安装的APK
        last_3_packages = get_packages_info(app_info['name'])
        if not last_3_packages:
            return False
        # 1. 搜索APP, 找到能下载APP的页面
        ok = search(input_text=app_info['name'])
        if not ok:
            print(f"Can't search app {app_info['name']}, you can try it again")
            return False
        # 2. 找到安装按钮
        ok = download_apk(app_info['name'])
        if not ok:
            print(f"Can't download app {app_info['name']}, you can try it again")
            return False
        
        # 3. 找到安装包位置
        new_3_packages = get_packages_info(app_info['name'])
        path_packages = find_new_apps(last_3_packages, new_3_packages)
        
        # 4. 把安装包传到 save_path 并将APK命名为 filename
        res = []
        for apk_path, apk_package_name in path_packages:
            self.operator.pull(apk_path, f'{save_dir}/{filename if filename else apk_package_name}.apk')
            res.append(f'{save_dir}/{filename if filename else apk_package_name}.apk')
            
            # 5. 卸载app 删除安装包
            self.operator.app_uninstall(apk_package_name)
            print(f"successfully download {app_info['name']}, save in {save_dir}/{filename if filename else apk_package_name}.apk")
        if not res:
            print(f"Install fialed of {app_info['name']}")
            return False
        return res

    def run_apks_spider(self, apps_info: List[Dict], save_dir: str, retry: int=3) -> List[Union[bool, List[str]]]:
        """
            爬取多个app的apk文件
            param apps_info: 多个app信息的列表
            return: 返回 list，每个item代表 apk 是否下载成功
        """
        def restart_play():
            """
                重启Google Play Store
            """
            self.operator.press_key(KEYCODE_HOME)
            self.operator.clear_background()
            self.operator.start_app(self.play_package, self.play_activity)
            time.sleep(2)

        res = []
        for index, app_info in enumerate(apps_info):
            # 重启APP
            restart_play()
            # 下载APK
            apk_path = None
            retry_count = 0
            while not apk_path and retry_count < retry:
                apk_path = self.run_apk_spider(app_info, save_dir)
                retry_count += 1
            apps_info[index].update({'apk_path': apk_path})
            res.append(apk_path)
            print("=" * 20, end='\n\n')
        df = pd.DataFrame(apps_info)
        df.to_excel(f'{save_dir}/desc.xlsx', index=False)
        return res


def download_apks():
    device = "127.0.0.1:7555"
    operator = MumuOperator(address=device.split(':')[0],
                            port=int(device.split(':')[1]))
    google_spiber = GoogleSpider(operator)
    
    df = pd.read_excel('./app_rank.xlsx', sheet_name='手机-社交')
    app_infos = [{'name': v} for _, v in df['Name'].to_dict().items()]
    google_spiber.run_apks_spider(apps_info=app_infos, save_dir='./results/社交/')


def rank_of():
    device = "127.0.0.1:7555"
    # 0. 确定爬取目标，类别、数量、地区
    target_list = [
            # ("手机", "办公"),
            # ("手机", "财务"),
            # ("手机", "餐饮美食"),
            # ("手机", "车辆和交通"),
            ("手机", "地图和导航"),
            ("手机", "个性定制"),
            # ("手机", "购物"),
            ("手机", "活动"),
            # ("手机", "家具装修"),
            ("手机", "健康与健身"),
            ("手机", "教育"),
            # ("手机", "漫画"),
            ("手机", "美容时尚"),
            # ("手机", "软件库与演示"),
            # ("手机", "社交"),
            # ("手机", "摄影"),
            ("手机", "生活时尚"),
            # ("手机", "视频播放和编辑"),
            # ("手机", "体育"),
            ("手机", "天气"),
            # ("手机", "通讯"),
            ("手机", "图书与工具书"),
            ("手机", "外出旅行与本地生活"),
            ("手机", "效率"),
            # ("手机", "新闻杂志"),
            ("手机", "医疗"),
            ("手机", "艺术和设计"),
            ("手机", "音乐与音频"),
            # ("手机", "娱乐"),
            # ("手机", "育儿"),
        ]
    # 连接设备
    operator = MumuOperator(address=device.split(':')[0],
                            port=int(device.split(':')[1]))
    # 初始化 spiber
    google_spiber = GoogleSpider(operator)
    # 设定目标
    # google_spiber.set_rank_target(target_list)
    # 开始
    # google_spiber.run_spider()    # 挨个爬取每个目标
    # google_spiber.rank_of('手机', '办公1')   # 仅爬取传入的目标

if __name__ == '__main__':
    download_apks()
