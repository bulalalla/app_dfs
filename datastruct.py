import xml.etree.ElementTree as ET
import re

Any = object

class UIElement:

    def __init__(self, element: ET.Element) -> None:
        # 把xml node的属性赋给此对象
        for key, value in element.attrib.items():
            k = key.replace('-', '_')
            v = value
            if k == 'class':
                k = 'ele_class'
            if v == 'true':
                self.__dict__.update({k: True})
            elif v == 'false':
                self.__dict__.update({k: False})
            else:
                self.__dict__.update({k: v})
        # print(self.__dict__)
        bounds_str = self.bounds
        numbers = re.findall(r'\d+', bounds_str)        
        self.bounds = ((int(numbers[0]), int(numbers[1])), (int(numbers[2]), int(numbers[3])))
        self.center = ((self.bounds[0][0] + self.bounds[1][0])/2, (self.bounds[0][1] + self.bounds[1][1])/2)
        # 尽管如此，此id仍然是不可信的
        self.id = (self.resource_id + bounds_str, self.resource_id + self.content_desc + self.text)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, UIElement):
            return self.id[1] == value.id[1]
        return False


class UI:

    def __init__(self, xml_str=None, xml_filename=None) -> None:
        self.xml_str = ''
        self.id_list = list()
        self.clickable_elements = list()
        self.scrollable_elements = list()
        self.long_clickable_elements = list()
        self.editable_elements = list()
        # 读取数据
        if xml_filename:
            # type(root_element) == xml.etree.ElementTree.Element
            root_element = ET.parse(xml_filename).getroot()
        else:
            root_element = ET.fromstring(xml_str)

        # 遍历整个dom树，遍历需要完成以下任务
        # 1. 遍历过程中应该给以下node创建元素：
        #    a. 针对clickable, scrollable, long clickable的元素，应该在遍历到的时候直接创建
        #    b. 针对 editable 元素，应该根据class是否为 xx.Edit创建
        #    c. 针对layout，不应该创建
        # 2. 生成元素，计算元素id，UI的id：UI的id应该根据叶子节点进行计算

        queue = list()
        queue.extend([child for child in root_element])     # 根元素hierarchy 不进入遍历
        while len(queue):
            # 获取队列第一个元素
            et_element = queue.pop()
            element = UIElement(element=et_element)
            # 对这个元素进行分类...
            if element.clickable:
                self.clickable_elements.append(element)
            if 'EditText' in element.ele_class:
                self.editable_elements.append(element)
            if element.scrollable:
                self.scrollable_elements.append(element)
            # 把这个元素的儿子添加到队列中
            children = [child for child in et_element]
            queue.extend(children)
            if len(children):
                # 如果没有子节点，那么这个节点应该作为UI id的一部分
                self.id_list.append(element.id)


    def __eq__(self, value: object) -> bool:
        if isinstance(value, UI):
            pass
        return False

# Android KeyCode
# 键名	 描述	 键值
# 电话键
KEYCODE_CALL = 5    # 拨号键
KEYCODE_ENDCALL = 6 # 挂机键
KEYCODE_HOME = 3    # 按键Home
KEYCODE_MENU = 82   # 菜单键
KEYCODE_APP_SWITCH = 187    # 切换APP
KEYCODE_BACK = 4    # 返回键
KEYCODE_SEARCH = 84 # 搜索键
KEYCODE_CAMERA = 27 # 拍照键
KEYCODE_FOCUS = 80  # 拍照对焦键
KEYCODE_POWER = 26  # 电源键
KEYCODE_NOTIFICATION = 83 # 通知键
KEYCODE_MUTE = 91   # 话筒静音键
KEYCODE_VOLUME_MUTE = 164 # 扬声器静音键
KEYCODE_VOLUME_UP = 24    # 音量增加键
KEYCODE_VOLUME_DOWN = 25  # 音量减小键

# 控制键
KEYCODE_ENTER = 66       # 回车键
KEYCODE_ESCAPE = 111     # ESC键
KEYCODE_DPAD_CENTER = 23 # 导航键 确定键
KEYCODE_DPAD_UP = 19     # 导航键 向上
KEYCODE_DPAD_DOWN = 20   # 导航键 向下
KEYCODE_DPAD_LEFT = 21   # 导航键 向左
KEYCODE_DPAD_RIGHT = 22  # 导航键 向右
KEYCODE_MOVE_HOME = 122  # 光标移动到开始键
KEYCODE_MOVE_END = 123   # 光标移动到末尾键
KEYCODE_PAGE_UP = 92     # 向上翻页键
KEYCODE_PAGE_DOWN = 93   # 向下翻页键
KEYCODE_DEL = 67         # 退格键
KEYCODE_FORWARD_DEL = 112# 删除键
KEYCODE_INSERT = 124     # 插入键
KEYCODE_TAB = 61         # Tab键
KEYCODE_NUM_LOCK = 143   # 小键盘锁
KEYCODE_CAPS_LOCK = 115  # 大写锁定键
KEYCODE_BREAK = 121      # Break/Pause键
KEYCODE_SCROLL_LOCK = 116# 滚动锁定键
KEYCODE_ZOOM_IN = 168    # 放大键
KEYCODE_ZOOM_OUT = 169   # 缩小键

# 组合键
# KEYCODE_ALT_LEFT         # Alt+Left
# KEYCODE_ALT_RIGHT        # Alt+Right
# KEYCODE_CTRL_LEFT        # Control+Left
# KEYCODE_CTRL_RIGHT       # Control+Right
# KEYCODE_SHIFT_LEFT       # Shift+Left
# KEYCODE_SHIFT_RIGHT      # Shift+Right

# 基本
KEYCODE_0 = 7    # 按键’0’
KEYCODE_1 = 8    # 按键’1’
KEYCODE_2 = 9    # 按键’2’
KEYCODE_3 = 10   # 按键’3’
KEYCODE_4 = 11   # 按键’4’
KEYCODE_5 = 12   # 按键’5’
KEYCODE_6 = 13   # 按键’6’
KEYCODE_7 = 14   # 按键’7’
KEYCODE_8 = 15   # 按键’8’
KEYCODE_9 = 16   # 按键’9’
KEYCODE_A = 29   # 按键’A’
KEYCODE_B = 30   # 按键’B’
KEYCODE_C = 31   # 按键’C’
KEYCODE_D = 32   # 按键’D’
KEYCODE_E = 33   # 按键’E’
KEYCODE_F = 34   # 按键’F’
KEYCODE_G = 35   # 按键’G’
KEYCODE_H = 36   # 按键’H’
KEYCODE_I = 37   # 按键’I’
KEYCODE_J = 38   # 按键’J’
KEYCODE_K = 39   # 按键’K’
KEYCODE_L = 40   # 按键’L’
KEYCODE_M = 41   # 按键’M’
KEYCODE_N = 42   # 按键’N’
KEYCODE_O = 43   # 按键’O’
KEYCODE_P = 44   # 按键’P’
KEYCODE_Q = 45   # 按键’Q’
KEYCODE_R = 46   # 按键’R’
KEYCODE_S = 47   # 按键’S’
KEYCODE_T = 48   # 按键’T’
KEYCODE_U = 49   # 按键’U’
KEYCODE_V = 50   # 按键’V’
KEYCODE_W = 51   # 按键’W’
KEYCODE_X = 52   # 按键’X’
KEYCODE_Y = 53   # 按键’Y’
KEYCODE_Z = 54   # 按键’Z’

# 测试使用
if __name__ == '__main__':
    with open('./dump2.xml', 'r', encoding='utf-8') as file:
        content = file.read()
    ui = UI(xml_str=content)
    print(ui.clickable_elements)
    print(ui.scrollable_elements)
    print(ui.editable_elements)
    # ele1 = UIElement()
    # ele2 = UIElement()
    # ele1.tag = 'a'
    # ele2.tag = 'b'
    # print(ele1.tag, ele2.tag)
    pass
