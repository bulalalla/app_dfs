import xml.etree.ElementTree as ET
import re
import hashlib

class UIElement:

    def __init__(self, element: ET.Element, xpath: str) -> None:
        self.xpath = xpath
        self.op_times = 0
        # 把xml node的属性赋给此对象
        for key, value in element.attrib.items():
            k = key.replace('-', '_')
            v = value
            if k == 'class':
                k = 'tag'
            if v == 'true':
                self.__dict__.update({k: True})
            elif v == 'false':
                self.__dict__.update({k: False})
            else:
                self.__dict__.update({k: v})
        # 处理bounds
        bounds_str = self.bounds
        numbers = re.findall(r'\d+', bounds_str)
        self.bounds = ((int(numbers[0]), int(numbers[1])), (int(numbers[2]), int(numbers[3])))
        self.center = ((self.bounds[0][0] + self.bounds[1][0]) / 2, (self.bounds[0][1] + self.bounds[1][1]) / 2)
        # 生成id
        # self.id = (self.resource_id + bounds_str, self.resource_id + self.content_desc + self.text)
        self.hash_value = self.compute_hash(xpath)

    def compute_hash(xpath: str) -> str:
        # 使用 SHA-256 算法计算哈希值
        return hashlib.sha256(xpath.encode('utf-8')).hexdigest()

    def __hash__(self):
        # 返回哈希值，方便集合或字典中使用
        return int(self.hash_value, 16)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, UIElement):
            return self.hash_value == other.hash_value
        return False


class ScreenUI:

    def __init__(self, xml_str=None, xml_filename=None, count_dict: dict = {}) -> None:
        self.id = None
        self.id_list = list()
        self.clickable_elements = list()
        self.scrollable_elements = list()
        self.long_clickable_elements = list()
        self.editable_elements = list()
        # 读取数据
        if xml_filename:
            root_element = ET.parse(xml_filename).getroot()
        else:
            root_element = ET.fromstring(xml_str)

        # 遍历整个dom树并计算xpath
        self._traverse(root_element, count_dict, xpath='')

    def _traverse(self, element, count_dict, xpath):
        for i, child in enumerate(element):
            child_xpath = f"{xpath}/{child.tag}[{i + 1}]"
            ui_element = UIElement(element=child, xpath=child_xpath)
            ui_element.op_times = count_dict.get(ui_element.id, 0)

            # 分类
            if ui_element.clickable:
                self.binary_insertion(ui_element, self.clickable_elements)
            if 'EditText' in ui_element.ele_class:
                self.binary_insertion(ui_element, self.editable_elements)
            if ui_element.scrollable:
                self.binary_insertion(ui_element, self.scrollable_elements)

            if not list(child):
                # 如果没有子节点，那么这个节点应该作为UI id的一部分
                self.id_list.append(ui_element)
            else:
                self._traverse(child, count_dict, child_xpath)

    def binary_insertion(self, element: UIElement, element_list: list[UIElement]):
        element_count = element.op_times
        left, right = 0, len(element_list)
        while left < right:
            mid = (left + right) // 2
            if element_list[mid].op_times < element_count:
                left = mid + 1
            else:
                right = mid
        while right < len(element_list) and element_list[right].op_times == element_count:
            right += 1
        element_list.insert(right, element)
        return element_list

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ScreenUI):
            eq_count = 0
            for ele1 in self.id_list:
                for ele2 in value.id_list:
                    if ele1 == ele2:
                        eq_count += 1
                        break
            return (eq_count * 2) / (len(self.id_list) + len(value.id_list)) > 0.9
        return False

# 测试使用
if __name__ == '__main__':
    with open('./dump2.xml', 'r', encoding='utf-8') as file:
        content = file.read()
    ui = ScreenUI(xml_str=content)
    with open('./dump3.xml', 'r', encoding='utf-8') as file:
        content = file.read()
    ui2 = ScreenUI(xml_str=content)

    print(ui.id_list)
    print(ui2.id_list)
    print(ui == ui2)
