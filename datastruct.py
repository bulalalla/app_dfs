import xml.etree.ElementTree as ET
import re

Any = object

class UIElement:

    def __init__(self, element: ET.Element) -> None:
        self.op_times = 0
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


class ScreenUI:

    def __init__(self, xml_str=None, xml_filename=None, count_dict: dict={}) -> None:
        self.id = None
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
            element.op_times = count_dict[element.id] if element.id in count_dict.keys() else 0
            if element.clickable:
                self.binary_insertion(element, self.clickable_elements)
            if 'EditText' in element.ele_class:
                self.binary_insertion(element, self.editable_elements)
            if element.scrollable:
                self.binary_insertion(element, self.scrollable_elements)
            # 把这个元素的儿子添加到队列中
            children = [child for child in et_element]
            queue.extend(children)
            if not len(children):
                # 如果没有子节点，那么这个节点应该作为UI id的一部分
                self.id_list.append(element.id)

    # TODO 折半插入，插入element，保持原有的数据
    def binary_insertion(element: UIElement, element_list: list[UIElement]):
        element_count = element.count

        # 定义二分查找的左右边界
        left, right = 0, len(element_list)
        while left < right:
            mid = (left + right) // 2
            if element_list[mid].count < element_count:
                left = mid + 1
            else:
                right = mid

        # 在right索引处插入元素
        while right < len(element_list) and element_list[right].count == element_count:
            right += 1
            
        element_list.insert(right, element)
        return element_list

    def sort(self, count_dict: dict):
        pass

    # TODO 使用树结构判断两个Screen是否相同
    def __eq__(self, value: object) -> bool:
        if isinstance(value, ScreenUI):
            eq_count = 0
            for id in self.id_list:
                for id2 in value.id_list:
                    if id[0] == id2[0]:
                        eq_count += 0.3
                        if id[1] == id2[1]:
                            eq_count += 0.7
                        break
                    elif id[1] == id2[1]:
                        eq_count += 1
                        break
            print((eq_count * 2)/(len(self.id_list) + len(value.id_list)))
            return (eq_count * 2)/(len(self.id_list) + len(value.id_list)) > 0.9
        return False

    # TODO 借助一些绘图工具，把识别到的组件绘制出来，背景是dump时的屏幕图片，此函数主要调试使用
    def show_screen(self, pos1, pos2):
        pass


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
    # ele1 = UIElement()
    # ele2 = UIElement()
    # ele1.tag = 'a'
    # ele2.tag = 'b'
    # print(ele1.tag, ele2.tag)
    pass
