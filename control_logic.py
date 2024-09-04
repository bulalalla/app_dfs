from bisect import bisect_right
import copy
from base_operation import *
from datastruct import *


class Controler:

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
        self.screen_record = dict()
        self.ui_element_record = dict()
        self.screen_count = 0
        self.ui_element_count = 0
        self.ui_element_op_times = list()
        self.address = address
        self.port = port
        self.app_package_name = app_package_name
        self.app_activity_name = app_activity_name
        self.max_depth = max_depth
        self.max_loop = max_loop
        self.operator = Operator(address=self.address, port=self.port)

    # TODO 判断当前界面是否包含此元素
    def has_element(self, element, op_type):
        now_screen = ScreenUI(self.operator.dump_screen_xml())
        for ele in now_screen[op_type]:
            if ele == element:
                return True
        return False

    # TODO 在点击操作开始之前，向文本框输入内容
    def edit_text_view(self, editable_list: list[UIElement], pre_text: dict):
        pass

    # TODO 在点击操作开始之前，滑动View
    def scroll_view(self, scroll_list: list[UIElement]):
        pass

    # TODO 点击元素
    def click_view(self, element: UIElement):
        # 1. 检查是否包含此元素
        if self.has_element(element):
            # 2. 根据1，决定是否执行点击操作
            self.operator.click(*element.center)
            return True
        return False
    
    # 关闭应用程序重新打开  这个函数应该放在 base_operation的类中，不同模拟机的实现不同，才能体现多态
    def clear_background(self):
        self.operator.press_key(KEYCODE_HOME)
        self.operator.press_key(KEYCODE_HOME)
        self.operator.press_key(KEYCODE_APP_SWITCH)
        content = self.operator.dump_screen_xml()
        # print(content)
        ui = ScreenUI(xml_str=content)
        for element in ui.clickable_elements:
            if '清除' in element.text:
                self.operator.click(*element.center)
                return True
            elif 'clear' in element.text:
                self.operator.click(*element.center)
                return True
        return False

    # TODO app自动遍历
    def app_dfs(self, screen: ScreenUI, curr_depth: int) -> None:
        if curr_depth > self.max_depth:
            return

        # 执行界面不会改变的操作
        self.edit_text_view(screen.editable_elements, {})
        self.scroll_view(screen.scrollable_elements)

        # 执行界面会改变的操作
        for element in screen.clickable_elements:
            # 是否点击成功
            if self.click_view(element):
                now_screen = ScreenUI(self.operator.dump_screen())
                if screen == now_screen:
                    continue
                # 否则 判断是否进入新的界面
                if now_screen not in self.screen_record.values():
                    self.screen_record[screen_count] = copy.deepcopy(now_screen)
                    screen_count += 1
                # 进入下一个界面继续执行
                self.app_dfs(now_screen, curr_depth + 1)
            # 点击失败
            else:
                continue

    def run(self):
        for _ in range(self.max_loop):
            self.clear_background()
            self.operator.start_app(self.app_package_name, self.app_activity_name)
            sleep(10)
            screen = ScreenUI(self.operator.dump_screen_xml())
            self.app_dfs(screen, 0)


if __name__ == '__main__':

    controler = Controler(Operator=MumuOperator, 
                          app_activity_name="",
                          app_package_name="")
    controler.run()
