from bisect import bisect_right
import copy
from base_operation import *
from datastruct import *


# TODO 传入升序表，返回操作次数最少的元素
def get_minimal_op_element(element_list: list):
    return element_list[0]

# TODO 在点击操作开始之前，向文本框输入内容
def edit_text_view(editable_list: list[UIElement], pre_text: dict):
    pass

# TODO 在点击操作开始之前，滑动View
def scroll_view(scroll_list: list[UIElement]):
    pass

# TODO 判断当前界面是否包含此元素
def has_element_now(element):
    pass

# TODO app自动遍历
def app_dfs(screen: ScreenUI, curr_depth: int) -> None:
    if curr_depth > max_depth:
        return

    edit_text_view(screen.editable_elements, {})
    scroll_view(screen.scrollable_elements)

    for element in screen.clickable_elements:
        pos = has_element_now(element)
        if pos:
            operator.click(*pos)
            now_screen_str = operator.dump_screen_xml()
            now_screen = ScreenUI(xml_str=now_screen_str)
            # 如果还在当前界面，执行下一个元素操作
            if screen == now_screen:
                continue
            # 否则 判断是否进入新的界面
            if now_screen not in screen_record.values():
                screen_record[screen_count] = copy.deepcopy(now_screen)
                screen_count += 1
            # 进入下一个界面继续执行
            app_dfs(now_screen, curr_depth + 1)

        else:
            continue




def run():
    pass



if __name__ == '__main__':
    # id都为自增的，即当检测到新的界面/元素，则id自增并分配给新的界面/元素
    # dict记录此id的信息，用于检测 界面/元素 是否为新的
    # list 记录 元素被操作的次数，每次都应该选择操作次数最少的进行操作，可以自行实现数据结构优化时间
    screen_record, screen_count = dict(), 0
    ui_element_id, ui_element_count, ui_element_op_times = dict(), 0, list()
    max_depth = 10

    operator = MumuOperator(address="127.0.0.1", port=7555)
    run()