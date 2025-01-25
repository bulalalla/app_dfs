# 保证能找到common
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import copy
from common.base_operation import *
from common.datastruct import *


class Controler:
    """
        Controler是对各个平台Operator的封装，应提供更高级的操作，如清理后台任务、登录账号、下载APP等
    """

    def __init__(self,
                 Operator,  # 一个Operator的类
                 address="127.0.0.1",
                 port=7555,
                 app_package_name="",
                 app_activity_name="",
                 max_depth=10,
                 max_loop=10,
                 ) -> None:
        # id都为自增的，即当检测到新的界面/元素，则id自增并分配给新的界面/元素
        # dict记录此id的信息，用于检测 界面/元素 是否为新的
        # list 记录 元素被操作的次数，每次都应该选择操作次数最少的进行操作，可以自行实现数据结构优化时间
        
        self.record = dict()
        """
            {
                "activity1": {
                    "id1": count1,
                    "id2": count2,
                    ...
                },
                "activity1": {
                    "id1": count1,
                    "id2": count2,
                    ...
                }
            }
        """
        # 基本信息
        self.address = address
        self.port = port
        self.app_package_name = app_package_name
        self.app_activity_name = app_activity_name
        self.begin_time = None

        # dfs超参数
        self.max_depth = max_depth
        self.max_loop = max_loop
        self.max_timeout = 10 * 60  # 10分钟

        # 初始化Operator
        self.operator = Operator(address=self.address, port=self.port)

    # TODO 判断当前界面是否包含此元素
    def has_element(self, element):
        now_screen = UIBlock(xml_str=self.operator.dump_hierarchy(), activity=self.operator.curr_app()["activity"])
        return now_screen.has_element(element)

    # TODO 在点击操作开始之前，向文本框输入内容
    def edit_text_view(self, editable_list: list[UIBlock], pre_text: dict):
        pass

    # TODO 在点击操作开始之前，滑动View
    def scroll_view(self, scroll_list: list[UIBlock]):
        pass

    # TODO 点击元素
    def click_view(self, activity, element: UIBlock):
        if self.operator.curr_app()["package"] != self.app_package_name:
            return False
        # 1. 检查是否包含此元素
        if self.has_element(element):
            # 2. 根据1，决定是否执行点击操作
            if element.id in self.record[activity].keys():
                self.record[activity][element.id] += 1
            else:
                self.record[activity][element.id] = 1
            self.operator.click(*element.center)
            return True
        return False

    # app自动遍历
    def app_dfs(self, curr_depth: int, curr_time) -> None:
        if curr_time - self.begin_time > self.max_timeout:
            return
        if curr_depth > self.max_depth:
            return
        if self.operator.curr_app()["package"] != self.app_package_name:
            return
        time.sleep(2)
        screen = UIBlock(xml_str=self.operator.dump_hierarchy(), activity=self.operator.curr_app()["activity"])

        # 执行界面不会跳转的操作
        self.edit_text_view(screen.editable_elements, {})
        self.scroll_view(screen.scrollable_elements)

        # 执行界面可能会跳转的操作
        clickable_ele = [(ele, self.record[screen.activity][ele.id] if ele.id in self.record[screen.activity] else 0 ) for ele in screen.clickable_elements]
        clickable_ele.sort(key=lambda x: x[1])  # 根据第二个元素升序排序
        for element, _ in clickable_ele:
            # 是否点击成功
            if self.click_view(screen.activity, element):
                curr_activity = self.operator.curr_app()['activity']
                if curr_activity != screen.activity:
                    if curr_activity not in self.record.keys():
                        self.record[curr_activity] = {}
                    self.app_dfs(curr_depth + 1, time.time())
                else:
                    self.app_dfs(curr_depth, time.time())
            # 点击失败
            else:
                continue

    def run(self):
        # 此时 抓包、中间人代理、app包名、启动activity都已确定。
        # 开始执行自动控制
        print("开始测试...")
        self.record = dict()    # 清空
        self.begin_time = time.time()

        for _ in range(self.max_loop):
            self.operator.clear_background()
            self.operator.start_app(self.app_package_name, self.app_activity_name)
            # 打开应用程序可能需要一点时间
            sleep(3)
            # 获取第一个界面，开始遍历
            self.record[self.app_activity_name] = {}
            self.app_dfs(0, time.time())
        print("测试结束.")
    

if __name__ == '__main__':
    c = Controler(Operator=MumuOperator, app_package_name="com.washingtonpost.android", app_activity_name="com.wapo.flagship.MainActivity")
    c.run()
