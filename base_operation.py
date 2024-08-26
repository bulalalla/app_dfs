from abc import abstractmethod, ABCMeta
from time import sleep
import uiautomator2 as u2

import datastruct as ds

SLEEP_AFTER_CLICK = 1

class BaseOperator(metaclass=ABCMeta):
    """
    定义操作类的接口，操作类目标是实现在不同Android设备上实现一些常用的基本操作
    Method click(): 传入(x, y)坐标，执行点击对应屏幕位置
    Method scroll(): 传入两个二维坐标，模拟手指从 (x1, y1) -> (x2, y2) 滑动
    Method input(): 给定一个目标，向其输入文本内容
    Method clear_background(): 执行一系列操作，模拟执行清理后台应用程序进程
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


class MumuOperator(BaseOperator):

    def __init__(self, device: u2.Device) -> None:
        if isinstance(device, u2.Device):
            self.device = device
        else:
            raise "device is not uiautomator2.Device object when create a BaseOperator object"

    def click(self, x: float | int, y: float | int):
        self.device.click(x, y)
        sleep(SLEEP_AFTER_CLICK)

    def scroll(self, x1, y1, x2, y2, duration=0.5):
        self.device.swipe(fx=x1, fy=y1, tx=x2, ty=y2, duration=duration)

    def input(self, text: str, x: float | int, y: float | int):
        self.click(x=x, y=y)
        self.device.send_keys(text=text, clear=True)

    def clear_background(self):
        self.device.press(ds.KEYCODE_HOME)
        sleep(1)
        self.device.press(ds.KEYCODE_APP_SWITCH)
        sleep(1)
        content = self.device.dump_hierarchy()
        # print(content)
        ui = ds.UI(xml_str=content)
        for element in ui.clickable_elements:
            if '清除' in element.text:
                self.click(*element.center)
            elif 'clear' in element.text:
                self.click(*element.center)


if __name__ == '__main__':
    d = u2.connect()
    print("begin")
    # mumu_op = MumuOperator(device=d)
    # mumu_op.clear_background()

    print("end")