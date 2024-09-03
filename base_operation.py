import os
from abc import abstractmethod, ABCMeta
from time import sleep
import uiautomator2 as u2

import datastruct as ds


class BaseOperator(metaclass=ABCMeta):
    """
    定义操作类的接口，操作类目标是实现在不同Android设备上实现一些常用的基本操作
    Method click(): 传入(x, y)坐标，执行点击对应屏幕位置
    Method scroll(): 传入两个二维坐标，模拟手指从 (x1, y1) -> (x2, y2) 滑动
    Method input(): 给定一个目标，向其输入文本内容
    Method clear_background(): 执行一系列操作，模拟执行清理后台应用程序进程
    Method press_key(): 模拟按压某个按键，如home键
    Method dump_screen(): 获取整个屏幕的xml
    """

    @abstractmethod
    def click():
        pass

    @abstractmethod
    def scroll():
        pass

    @abstractmethod
    def input():
        pass

    @abstractmethod
    def clear_background():
        pass

    @abstractmethod
    def press_key():
        pass

    @abstractmethod
    def dump_screen():
        pass


class MumuOperator(BaseOperator):

    SLEEP_AFTER_CLICK = 1

    def __init__(self, address="127.0.0.1", port=7555, serial=None) -> None:
        try:
            os.popen(f"adb connect {address}:{port}")
            self.device = u2.connect()
        except Exception as e:
            raise f"Exception captured when create MumuOperator object: {e.message}"

    def click(self, x: float | int, y: float | int):
        self.device.click(x, y)
        sleep(self.SLEEP_AFTER_CLICK)

    def scroll(self, x1, y1, x2, y2, duration=0.5):
        self.device.swipe(fx=x1, fy=y1, tx=x2, ty=y2, duration=duration)

    def input(self, text: str, x: float | int, y: float | int):
        self.click(x=x, y=y)
        self.device.send_keys(text=text, clear=True)

    def clear_background(self):
        self.device.press(KEYCODE_HOME)
        self.press_key(KEYCODE_HOME)
        self.press_key(KEYCODE_APP_SWITCH)
        content = self.device.dump_hierarchy()
        # print(content)
        ui = ds.UI(xml_str=content)
        for element in ui.clickable_elements:
            if '清除' in element.text:
                self.click(*element.center)
            elif 'clear' in element.text:
                self.click(*element.center)
    
    def press_key(self, keycode):
        self.device.press(keycode)
        sleep(self.SLEEP_AFTER_CLICK)

    def screenshot(self,
                    filename: str | None = None,
                    format: str = "pillow",
                    display_id: int | None = None):
        return self.device.screenshot(filename, format, display_id)
    
    def dump_screen_xml(self, compressed, pretty, max_depth):
        return self.device.dump_hierarchy(compressed, pretty, max_depth)


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


if __name__ == '__main__':
    d = u2.connect()
    print("begin")
    # mumu_op = MumuOperator(device=d)
    # mumu_op.clear_background()

    print("end")