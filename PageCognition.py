import cv2
import os
from datetime import datetime
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont

from Rect import Rect
from XML import XML
from Utils import get_bounds_average_color, get_inverse_color
from Driver import Driver


# 获取当前脚本文件目录
script_dir = os.path.dirname(os.path.abspath(__file__))
blank = 5
text_widths, text_height = [20, 40, 60], 35
font_path = os.path.join(script_dir, "Assets", "Arial.ttf")


class PageCognition:
    @staticmethod
    def draw_SoM(img_path: str = None, xml_path: str = None) -> Tuple[str, Dict]:
        assert((img_path is None and xml_path is None) or (img_path is not None and xml_path is not None)), "img_path and xml_path must be provided together"

        if img_path is None and xml_path is None:
            current_script_path = os.path.abspath(__file__)
            project_root = os.path.dirname(current_script_path)
            log_path = os.path.join(project_root, "UIAnalyzer_logs")
            os.makedirs(log_path, exist_ok=True)
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            img_path = os.path.join(log_path, f"{current_time}.png")
            xml_path = os.path.join(log_path, f"{current_time}.xml")

            driver = Driver()
            driver.screenshot(img_path)
            driver.get_xml(xml_path)

        xml = XML(xml_path)
        rects = xml.group_interactive_nodes()
        return PageCognition.__draw_rects(img_path, rects, "SoM")

    @staticmethod
    def grid(img_path: str) -> Tuple[str, Dict]:
        """切割为网格"""
        # 网格的行数和列数，经验值，可以进行配置
        rows = 12
        cols = 8

        # form the rects
        rects = []
        image = cv2.imread(img_path)
        height, width, _ = image.shape

        # 计算单元格的高度和宽度
        unit_height = height / rows
        unit_width = width / cols

        for i in range(rows):
            for j in range(cols):
                rect = dict()
                rect['bounds'] = [int(j * unit_width), int(i * unit_height), int((j + 1) * unit_width), int((i + 1) * unit_height)]
                rects.append(rect)

        return PageCognition.__draw_rects(img_path, rects, "grid")

    @staticmethod
    def __draw_rects(img_path: str, rects: List[Dict], extension_name: str) -> Tuple[str, Dict]:
        """
        绘制矩形和ID
        """
        assert(extension_name in ["SoM", "grid"]), f"Invalid extension name: {extension_name}"

        SoM = (extension_name == "SoM")
        img = Image.open(img_path)
        w, h = img.size[0], img.size[1]
        draw = ImageDraw.Draw(img)
        ret_rects = dict()
        for index, rect in enumerate(rects):
            rect_w, rect_h = rect['bounds'][2] - rect['bounds'][0], rect['bounds'][3] - rect['bounds'][1]
            if rect['bounds'][2] >= rect['bounds'][0] and rect['bounds'][3] >= rect['bounds'][1]:
                if (SoM and (rect_w < (w / 2) or rect_h < (h / 2)) and rect['bounds'][1] > (h / 50)) or not SoM:  # 1.过滤大框 + 2.过滤顶部状态栏元素
                    # rectangle
                    bound_color = get_inverse_color(get_bounds_average_color(img_path, rect['bounds']))
                    draw.rectangle(rect['bounds'], outline=bound_color, width=3)

                    # text
                    text_width = text_widths[0 if index < 10 else 1 if index < 100 else 2]
                    if SoM:
                        width_start = max(rect['bounds'][0], 0)
                        height_start = max(rect['bounds'][1] - text_height, 0)
                        rect['id_bounds'] = [width_start, height_start, width_start + text_width, height_start + text_height]
                    else:
                        rect['id_bounds'] = [rect['bounds'][0] + blank, rect['bounds'][1] + blank, rect['bounds'][0] + blank + text_width, rect['bounds'][1] + blank + text_height]
                    draw.rectangle(rect['id_bounds'], fill=(0, 0, 255), width=3)
                    draw.text((rect['id_bounds'][0], rect['id_bounds'][1]), str(index), fill=(0, 255, 0), font=ImageFont.truetype(font=font_path, size=35))
                    ret_rects[index] = rect

        directory, filename = os.path.split(img_path)
        name, extension = os.path.splitext(filename)
        SoM_file_path = os.path.join(directory, f"{name}_{extension_name}{extension}")
        img.save(SoM_file_path)

        return SoM_file_path, ret_rects
