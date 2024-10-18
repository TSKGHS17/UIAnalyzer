import os
import xml.etree.ElementTree as ET
from lxml import etree
from typing import List, Union, Dict
from anytree import Node, RenderTree

from .Driver import Driver
from .Utils import RED, END


class XML:
    """
    XML工具类
    """
    def __init__(self, path: str):
        self.xml_save_path = path
        try:
            self.root = self.__get_xml_root()
            if self.root is None:
                raise Exception(RED + "XML根节点获取失败" + END)
        except Exception as e:
            print("Error occurred when getting dom tree: " + str(e))
            raise

    def __get_xml_root(self) -> ET.Element:
        """
        获得domtree的根节点
        """
        try:
            domtree = ET.parse(self.xml_save_path)
            root = domtree.getroot()
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

    @staticmethod
    def build_tree(root: ET.Element) -> Node:
        def build_subtree(element: ET.Element, parent: Node = None) -> Node:
            element_node = Node(element, parent)
            element_node.xml_node = element
            for element_child in element:
                build_subtree(element_child, element_node)
            return element_node

        root_node = build_subtree(root)
        return root_node

    def group_interactive_nodes(self) -> List:
        def is_clickable(node: Node) -> bool:
            return node.xml_node.attrib.get('clickable', 'false') == 'true'

        def is_layout(node: Node) -> bool:
            attrib_class = node.xml_node.attrib.get('class', None)
            return attrib_class is not None and attrib_class.split('.')[-1] in ['ViewGroup', 'LinearLayout', 'FrameLayout', 'RelativeLayout']

        def is_leaf(node: Node) -> bool:
            return len(node.children) == 0

        def get_descendants(node: Node) -> List:
            descendants = []

            def collect_descendants(current_node: Node):
                for child in current_node.children:
                    descendants.append(child)
                    collect_descendants(child)

            collect_descendants(node)
            return descendants

        def group_subtree(node: Node) -> None:
            text = [] if node.xml_node.attrib['text'] == "" else [node.xml_node.attrib['text']]
            content_desc = [] if node.xml_node.attrib['content-desc'] == "" else [node.xml_node.attrib['content-desc']]
            resource_id = [] if node.xml_node.attrib['resource-id'] == "" else [node.xml_node.attrib['resource-id']]
            bounds = self.__parse_bounds(node.xml_node.attrib['bounds'])
            node_descendants = get_descendants(node)

            for descendant in node_descendants:
                if descendant.xml_node.attrib['text']:
                    text.append(descendant.xml_node.attrib['text'])
                if descendant.xml_node.attrib['content-desc']:
                    content_desc.append(descendant.xml_node.attrib['content-desc'])
                if descendant.xml_node.attrib['resource-id']:
                    resource_id.append(descendant.xml_node.attrib['resource-id'])
                descendant_bounds = self.__parse_bounds(descendant.xml_node.attrib['bounds'])
                # if descendant_bounds:
                #     bounds = [min(bounds[0], descendant_bounds[0]), min(bounds[1], descendant_bounds[1]), max(bounds[2], descendant_bounds[2]), max(bounds[3], descendant_bounds[3])]

            subtree = {"class": node.xml_node.attrib['class'].split('.')[-1], "resource_id": resource_id, "text": text, "content_desc": content_desc, "bounds": bounds}
            interactive_groups.append({key: value for key, value in subtree.items() if value not in ("", [])})

        def DFS(node: Node) -> None:
            if is_layout(node):
                if is_clickable(node):  # 1. For a clickable layout that contains no nested clickable layouts, group all its children
                    no_nested_clickable_layout = True
                    for child in node.children:
                        if is_layout(child) and is_clickable(child):
                            no_nested_clickable_layout = False
                            break

                    if no_nested_clickable_layout:
                        group_subtree(node)
                else:  # 2. A non-clickable layout has all its children as leaves, and at least one of them is clickable
                    all_child_leave = True
                    at_least_clickable = False
                    for child in node.children:
                        at_least_clickable = at_least_clickable or is_clickable(child)
                        if not is_leaf(child):
                            all_child_leave = False
                            break

                    if all_child_leave and at_least_clickable:
                        group_subtree(node)
            elif is_clickable(node):  # 3. a clickable widget can be grouped by itself
                attrib = node.xml_node.attrib
                bounds = self.__parse_bounds(attrib['bounds'])
                if bounds:
                    element = {"class": attrib['class'].split('.')[-1], "resource_id": attrib['resource-id'], "text": attrib['text'], "content_desc": attrib['content-desc'], "bounds": bounds}
                    interactive_groups.append({key: value for key, value in element.items() if value not in ("", [])})

            for child in node.children:
                DFS(child)

        interactive_groups = []
        root = self.build_tree(self.root)
        DFS(root)
        return interactive_groups

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


if __name__ == "__main__":
    xml = XML("Example/dom_tree.xml", driver=Driver())
    nodes = xml.group_interactive_nodes()
    for n in nodes:
        print(n)
