import lxml.etree as etree
import lxml
import lxml.etree
import uiautomator2 as u2
from typing import Optional, Union, Tuple, Dict, List
import hashlib
import functools
import time
import re
import os


def safe_xmlstr(s: str) -> str:
    s = re.sub('[$@#&]', '.', s)
    s = re.sub('\\.+', '.', s)
    s = re.sub('^\\.|\\.$', '', s)
    return s

def str2bytes(v: Union[str, bytes]) -> bytes:
    if isinstance(v, bytes):
        return v
    return v.encode("utf-8")


class ScreenShot():
    """
        表示一块 xml 树的信息
    """
    def __init__(self, xml_str: str=None, xml_filename: str="", lxml_element: lxml.etree._Element=None) -> None:
        if os.path.exists(xml_filename):
            element = etree.parse(xml_filename).getroot()
        elif xml_str is not None:
            element = etree.fromstring(text=str2bytes(xml_str))
        elif lxml_element is not None:
            element = lxml_element
        else:
            raise ValueError("Either xml_str or xml_filename or lxml_element must be provided.")
        
        # 将所有节点的tag name换成class的内容
        for node in element.xpath("//node"):
            node.tag = safe_xmlstr(node.attrib.pop("class", "")) or "node"

        # _ElementTree对象
        self._etree: etree._ElementTree = etree.ElementTree(element)
        self.root_element: etree._Element = element

        # 页面id
        self.id_list = []
        self.id: str=None
    
    @functools.cached_property
    def bounds(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        bounds_str = self.attrib.get('bounds', '[0,0][0,0]')
        numbers = re.findall(r'\d+', bounds_str)
        return ((int(numbers[0]), int(numbers[1])), (int(numbers[2]), int(numbers[3])))

    @functools.cached_property
    def center(self) -> Tuple[int, int]:
        return ((self.bounds[0][0] + self.bounds[1][0]) / 2, (self.bounds[0][1] + self.bounds[1][1]) / 2)

    @functools.cached_property
    def tag(self):
        return self.root_element.tag

    @functools.cached_property
    def attrib(self):
        return self.root_element.attrib

    @functools.cached_property
    def text(self):
        return self.root_element.text

    @functools.cached_property
    def tail(self):
        return self.root_element.tail

    @functools.cached_property
    def clickable_elements(self):
        return self.xpath('.//*[@clickable="true"]')
    
    @functools.cached_property
    def checkable_elements(self):
        return self.xpath('.//*[@checkable="true")]')
    
    @functools.cached_property
    def scrollable_elements(self):
        return self.xpath('.//*[@scrollable="true")]')
    
    @functools.cached_property
    def long_clickable_elements(self):
        return self.xpath('.//*[@long-clickable="true")]')
    
    @functools.cached_property
    def editable_elements(self):
        return self.xpath('.//*[contains(name(), "EditText")]')
    
    def getroot(self):
        """
            wrapper
        """
        return self.root_element
    
    @functools.cached_property
    def root_element(self):
        return self._etree.getroot()

    @functools.cached_property
    def id(self):
        """
            页面的id，请在访问过 self.elements后或调用 self._traverse()后，再访问此值
        """
        pass
        return         
        
    def __eq__(self, value: object) -> bool:
        if isinstance(value, ScreenShot):
            eq_count = 0
            for ele1 in self.id_list:
                for ele2 in value.id_list:
                    if ele1 == ele2:
                        eq_count += 1
                        break
            return (eq_count * 2) / (len(self.id_list) + len(value.id_list)) > 0.9
        return False

    def xpath(self, path):
        et_element = self._etree.xpath(path)
        if et_element is not None:
            if isinstance(et_element, list):
                return [ScreenShot(lxml_element=ele) for ele in et_element]
            return ScreenShot(lxml_element=et_element)
        return None

    def find(self, path, namespaces: Dict[str, str] | None = None):
        """
            在屏幕中查找某个元素
        """
        et_element = self._etree.find(path=path, namespaces=namespaces)
        if et_element is not None:
            return ScreenShot(lxml_element=et_element)
        return None

    def findall(self, path, namespaces: Dict[str, str] | None = None):
        """
            在屏幕中查找多个元素
        """
        et_elements = self._etree.findall(path=path, namespaces=namespaces)
        results = []
        for et_element in et_elements:    
            results.append(ScreenShot(lxml_element=et_element))
        if len(results):
            return results
        return None
    
    def findtext(self, path, default=None, namespaces: Dict[str, str] | None = None):
        """
            查找第一个text匹配的元素
        """
        et_element = self._etree.findtext(path=path, default=default, namespaces=namespaces)
        if et_element is not None:
            return ScreenShot(lxml_element=et_element)
        return None

    # TODO 一个绝对路径可以加一些
    def find_by(self, xpath: str, by: str) -> Optional[etree.Element]:
        # 拆分XPath路径
        path_parts = self._parse_xpath(xpath)
        
        # 从根节点开始按顺序查找
        current_node = self.root_element
        for part in path_parts:
            class_name, index = part
            # 查找该节点下符合 class 的所有子节点
            found = False
            for i, child in enumerate(current_node.findall('.//node')):
                if child.get('class') == class_name:
                    if i == index:  # 通过索引匹配
                        current_node = child
                        found = True
                        break
            if not found:
                return None  # 如果没有找到匹配的节点，则返回 None
        return current_node


def parse_xpath(xpath: str):
    """解析XPath，提取每一部分的 class 和索引"""
    parts = xpath.strip('/').split('/')
    parsed_parts = []
    for part in parts:
        # 匹配类似 android.widget.FrameLayout[1] 的部分
        match = re.match(r'([a-zA-Z0-9\.]+)\[(\d+)\]', part)
        if match:
            class_name = match.group(1)
            index = int(match.group(2)) - 1  # XPath索引是从1开始，Python是从0开始
            parsed_parts.append((class_name, index))
    return parsed_parts


def wait_until(operator: u2.Device, xpath: str, timeout=10, retry=3) -> Optional[ScreenShot]:
    """
        等待屏幕直到出现某个元素，将屏幕对象返回
        param operator: 设备操作器
        param xpath: 所等待元素的xpath
        param timeout: 等待最长时间
        param retry: 重试次数
        return None/ScreenShot()
    """
    print(f"Waiting for {xpath}")
    for _ in range(retry):
        start_time = time.time()
        while True:
            screen = ScreenShot(xml_str=operator.dump_hierarchy())
            ele = screen.find(path=xpath)
            if ele is not None:
                print(f"Found {xpath}")
                return screen
            if time.time() - start_time >= timeout:
                break
            time.sleep(0.5)
    print(f"Timeout for {xpath}")
    return None


# 测试使用
if __name__ == '__main__':
    d = u2.connect()

    s = ScreenShot(xml_str=d.dump_hierarchy())
    for ele in s.editable_elements:
        print(ele.tag, ele.text)

    ui = wait_until(d, './/androidx.compose.ui.platform.ComposeView[1]/android.view.View[1]/android.view.View[3]/android.view.View[1]/android.view.View[2]/android.widget.TextView[1]')
    if ui is not None:
        ele = ui.find('.//androidx.compose.ui.platform.ComposeView[1]/android.view.View[1]/android.view.View[3]/android.view.View[1]/android.view.View[2]/android.widget.TextView[1]')
        print(f"找到, {ele.attrib['text']}")
    else:
        print("未找到")