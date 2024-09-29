from bisect import bisect_right
import copy
from base_operation import *
from datastruct import *



class Controler:
    """
        Controler是对Operator的封装，提供更高级的操作，如清理后台任务、登录账号、下载APP等
    """

    def __init__(self,
                 Operator,
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
        self.screen_record = list()
        self.ui_element_record = list()
        # self.screen_count = 0
        # self.ui_element_count = 0
        self.ui_element_op_times = dict()
        self.address = address
        self.port = port
        self.app_package_name = app_package_name
        self.app_activity_name = app_activity_name
        self.max_depth = max_depth
        self.max_loop = max_loop
        self.operator = Operator(address=self.address, port=self.port)

    # TODO 判断当前界面是否包含此元素
    def has_element(self, element):
        now_screen = ScreenUI(count_dict=self.ui_element_op_times, xml_str=self.operator.dump_screen_xml())
        return now_screen.has_element(element)

    # TODO 在点击操作开始之前，向文本框输入内容
    def edit_text_view(self, editable_list: list[UIElement], pre_text: dict):
        pass

    # TODO 在点击操作开始之前，滑动View
    def scroll_view(self, scroll_list: list[UIElement]):
        pass

    # TODO 点击元素
    def click_view(self, element: UIElement):
        if self.operator.curr_app()["package"] != self.app_package_name:
            return False
        # 1. 检查是否包含此元素
        if self.has_element(element):
            # 2. 根据1，决定是否执行点击操作
            if element.hash_value in self.ui_element_op_times.keys():
                self.ui_element_op_times[element.hash_value] += 1
            else:
                self.ui_element_op_times[element.hash_value] = 1
            self.operator.click(*element.center)
            return True
        return False
    
    # 关闭应用程序重新打开  这个函数应该放在 base_operation的类中，不同模拟机的实现不同，才能体现多态
    def clear_background(self):
        self.operator.press_key(KEYCODE_HOME)
        self.operator.press_key(KEYCODE_APP_SWITCH)
        content = self.operator.dump_screen_xml()
        # print(content)
        ui = ScreenUI(count_dict=self.ui_element_op_times, xml_str=content)
        for element in ui.clickable_elements:
            if '清除' in element.text:
                self.operator.click(*element.center)
                return True
            elif 'clear' in element.text:
                self.operator.click(*element.center)
                return True
        self.operator.press_key(KEYCODE_HOME)
        return False

    # TODO app自动遍历
    def app_dfs(self, screen: ScreenUI, curr_depth: int) -> None:
        if curr_depth > self.max_depth:
            return
        if self.operator.curr_app()["package"] != self.app_package_name:
            return False

        # 执行界面不会改变的操作
        self.edit_text_view(screen.editable_elements, {})
        self.scroll_view(screen.scrollable_elements)

        # 执行界面会改变的操作
        for element in screen.clickable_elements:
            # 是否点击成功
            if self.click_view(element):
                now_screen = ScreenUI(count_dict=self.ui_element_op_times, xml_str=self.operator.dump_screen_xml())
                if screen == now_screen:
                    continue
                # 否则 判断是否进入新的界面
                if now_screen not in self.screen_record:
                    self.screen_record.append(copy.deepcopy(now_screen)) 
                # 进入下一个界面继续执行
                self.app_dfs(now_screen, curr_depth + 1)
            # 点击失败
            else:
                continue

    def run(self):
        # 此时 抓包、中间人代理、app包名、启动activity都已确定。
        # 开始执行自动控制
        print("开始测试...")
        for _ in range(self.max_loop):
            self.clear_background()
            self.operator.start_app(self.app_package_name, self.app_activity_name)
            # 打开应用程序可能需要一点时间
            sleep(20)
            
            screen = ScreenUI(count_dict=self.ui_element_op_times, xml_str=self.operator.dump_screen_xml())
            self.app_dfs(screen, 0)
        print("测试结束.")
    
