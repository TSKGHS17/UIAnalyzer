import os
import xml.etree.ElementTree as ET
from lxml import etree
from typing import List, Union

from Driver import Driver
from Utils import RED, END


class XML:
    """
    XML工具类
    """
    def __init__(self, path: str, driver: Driver):
        self.xml_save_path = path
        self.driver = driver
        try:
            self.root = self.__get_domtree()
            if self.root is None:
                raise Exception(RED + "XML根节点获取失败" + END)
        except Exception as e:
            print("Error occurred when getting dom tree: " + str(e))
            raise

    def __get_domtree(self) -> ET.Element:
        """
        获得domtree的根节点
        """
        folder_path = os.path.dirname(self.xml_save_path)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        self.driver.get_xml(self.xml_save_path)

        # parse XML
        try:
            tree = ET.parse(self.xml_save_path)
            root = tree.getroot()
            self.__format_and_write_back_xml()
            return root
        except Exception as e:
            raise Exception(f"Failed to parse XML: {e}")
            
    @staticmethod
    def __parse_bounds(bounds: Union[str, List]) -> List:
        """
        parse string into tuple
        """
        if isinstance(bounds, list):
            return bounds

        bounds = bounds.split("][")
        bounds = eval("[" + bounds[0] + "],[" + bounds[1] + "]")
        rect = [int(bounds[0][0]), int(bounds[0][1]), int(bounds[1][0]), int(bounds[1][1])]

        if rect[2] < rect[0] or rect[3] < rect[1]:
            return []
        else:
            return rect

    def __get_dom_list(self, root: ET.Element, dom_list: List) -> None:
        dom_list.append(root)
        for child in root:
            self.__get_dom_list(child, dom_list)

    def get_actionable_nodes(self) -> List:
        """
        获得页面的可点击节点
        """
        dom_list = []
        self.__get_dom_list(self.root, dom_list)

        one_pass = []
        for node in dom_list:
            if node.tag == 'node':
                if ("com.android.systemui" not in (node.attrib["resource-id"] if 'resource-id' in node.attrib else {})) and ("com.android.systemui" not in (node.attrib["package"] if 'package' in node.attrib else {})):
                    one_pass.append(node)

        # get actionable_nodes
        actionable_nodes = []
        for node in one_pass:
            if node.attrib['clickable'] == 'true':
                children = []
                self.__get_dom_list(node, children)

                # 把clickable节点的孩子聚合到这个节点：添加text和content-desc的信息
                if node.attrib['text'] == "":
                    for child in children:
                        node.attrib['text'] += child.attrib['text']
                        
                if node.attrib['content-desc'] == "":
                    for child in children:
                        node.attrib['content-desc'] += child.attrib['content-desc']
                        
                actionable_nodes.append(node)

        re = []
        for node in actionable_nodes:
            if node.attrib['text'] != '' or node.attrib['content-desc'] != '':
                text = node.attrib['text'].replace(" ", "")
                content_desc = node.attrib['content-desc'].replace(" ", "")
                if text != content_desc:
                    if text in content_desc:
                        info = node.attrib['content-desc']
                    elif content_desc in text:
                        info = node.attrib['text']
                    else:
                        info = node.attrib['content-desc'] + node.attrib['text']
                else:
                    info = node.attrib['content-desc'] if node.attrib['content-desc'] != '' else node.attrib['text']

                # node是输入框
                if node.attrib['class'] == "android.widget.EditText":
                    info = "(输入框) " + info

                bounds = self.__parse_bounds(node.attrib['bounds'])
                if len(bounds) > 0:
                    re.append({'info': info.replace(" ", ""), 'bounds': bounds, "type": "xml"})
            # 是否要XML文本为空的组件
            else:
                bounds = self.__parse_bounds(node.attrib['bounds'])
                if len(bounds) > 0:
                    re.append({'info': "", 'bounds': bounds, "type": "xml"})

        re = sorted(re, key=lambda r: (r['bounds'][1], r['bounds'][0]))
        return re

    def __format_and_write_back_xml(self) -> None:
        """
        整理xml文件
        """
        with open(self.xml_save_path, 'rb') as file:
            xml_content = file.read()

        parser = etree.XMLParser(remove_blank_text=True)
        xml_tree = etree.fromstring(xml_content, parser)

        formatted_xml = etree.tostring(xml_tree, pretty_print=True, encoding='utf-8', xml_declaration=True)

        with open(self.xml_save_path, 'wb') as file:
            file.write(formatted_xml)
