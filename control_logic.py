from base_operation import *
from datastruct import *


# TODO 传入升序表，返回操作次数最少的元素
def get_minimal_op_element(element_list: list):
    return element_list[0]


# TODO 折半插入，插入element，保持原有的数据
def insert_bin(element: UIElement, target_list: list[UIElement]):
    index = -1

# TODO app自动遍历
def app_dfs(screen: ScreenUI, curr_depth: int, max_depth: int) -> None:
    if curr_depth > max_depth:
        return
    


def run():
    operator = MumuOperator(address="127.0.0.1", port=7555)



if __name__ == '__main__':
    # id都为自增的，即当检测到新的界面/元素，则id自增并分配给新的界面/元素
    # dict记录此id的信息，用于检测 界面/元素 是否为新的
    # list 记录 元素被操作的次数，每次都应该选择操作次数最少的进行操作，可以自行实现数据结构优化时间
    screen_id, screen_count = dict(), 0
    ui_element_id, ui_element_count, ui_element_op_times = dict(), 0, list()

    run()