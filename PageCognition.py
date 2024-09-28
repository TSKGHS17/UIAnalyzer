import cv2
import os
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw, ImageFont

from Rect import Rect
from XML import XML
from Utils import get_bounds_average_color, get_inverse_color
from Driver import Driver


# 获取当前脚本文件目录
script_dir = os.path.dirname(os.path.abspath(__file__))
blank = 5
text_width, text_height = 54, 35
font_path = os.path.join(script_dir, "Assets", "Arial.ttf")


class PageCognition:
    @staticmethod
    def draw_SoM(img_path: str, xml_path: str, driver: Driver) -> Tuple[str, Dict]:
        xml = XML(xml_path, driver)
        xml_rects = xml.get_actionable_nodes()

        # 去除宽或高上，占整个屏幕的大矩形
        image = cv2.imread(img_path)
        height, width, _ = image.shape
        threshold = 0.8

        remove = set()
        for xml_rect in xml_rects:
            if Rect.iou_threshold(xml_rect['bounds'], [0, 0, width, height], threshold):
                remove.add(xml_rects.index(xml_rect))
            elif xml_rect['bounds'][0] == 0 and xml_rect['bounds'][2] == width:
                remove.add(xml_rects.index(xml_rect))
            elif xml_rect['bounds'][1] == 0 and xml_rect['bounds'][3] == height:
                remove.add(xml_rects.index(xml_rect))

        xml_rects = [xml_rect for i, xml_rect in enumerate(xml_rects) if i not in remove]

        rects = sorted(xml_rects, key=lambda r: (r['bounds'][1], r['bounds'][0]))
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
                rect['bounds'] = [int(j * unit_width), int(i * unit_height), int((j + 1) * unit_width),
                                  int((i + 1) * unit_height)]
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

        count = 0
        ret_rects = dict()
        for rect in rects:
            if SoM:
                width_start = max(rect['bounds'][0] - text_width, 0)
                height_start = max(rect['bounds'][1] - text_height, 0)
                rect['id_bounds'] = [width_start, height_start, width_start + text_width, height_start + text_height]
            else:
                rect['id_bounds'] = [rect['bounds'][0] + blank, rect['bounds'][1] + blank, rect['bounds'][0] + blank + text_width, rect['bounds'][1] + blank + text_height]

        if SoM:
            for index, rect in enumerate(rects):
                rect['id'] = index
            rects, _ = PageCognition.__merge_ID_overlay_rects(rects, len(rects))

        for rect in rects:
            rect_w, rect_h = rect['bounds'][2] - rect['bounds'][0], rect['bounds'][3] - rect['bounds'][1]
            if rect['bounds'][2] >= rect['bounds'][0] and rect['bounds'][3] >= rect['bounds'][1]:
                if (SoM and (rect_w < (w / 2) or rect_h < (h / 2)) and rect['bounds'][1] > (h / 50)) or not SoM:  # 1.过滤大框 + 2.过滤顶部状态栏元素
                    # rectangle
                    bound_color = get_inverse_color(get_bounds_average_color(img_path, rect['bounds']))
                    draw.rectangle(rect['bounds'], outline=bound_color, width=3)

                    # text
                    draw.rectangle(rect['id_bounds'], fill=(0, 0, 255), width=3)
                    draw.text((rect['id_bounds'][0], rect['id_bounds'][1]), str(count), fill=(0, 255, 0), font=ImageFont.truetype(font=font_path, size=35))
                    ret_rects[count] = rect
                    count += 1

        directory, filename = os.path.split(img_path)
        name, extension = os.path.splitext(filename)
        SoM_file_path = os.path.join(directory, f"{name}_{extension_name}{extension}")
        img.save(SoM_file_path)

        return SoM_file_path, ret_rects

    @staticmethod
    def __merge_ID_overlay_rects(rects: List, next_id: int) -> Tuple[List, int]:
        merged = True
        while merged:
            merged = False
            new_rects = []
            skip_indices = set()

            for rect1 in rects:
                for rect2 in rects:
                    if rect1['id'] not in skip_indices and rect2['id'] not in skip_indices and rect1['id'] != rect2['id']:
                        if Rect.is_overlap(rect1['id_bounds'], rect2['id_bounds']) or Rect.is_containing(
                                rect1['id_bounds'], rect2['id_bounds']) or Rect.is_containing(rect2['id_bounds'], rect1['id_bounds']):
                            new_rect = {
                                'info': rect1['info'] if rect1['info'] == rect2['info'] else rect1['info'] + rect2['info'],
                                'bounds': [min(rect1['bounds'][0], rect2['bounds'][0]),
                                           min(rect1['bounds'][1], rect2['bounds'][1]),
                                           max(rect1['bounds'][2], rect2['bounds'][2]),
                                           max(rect1['bounds'][3], rect2['bounds'][3])],
                                'type': 'bounds',
                                'id': next_id
                            }
                            # print(rect1, rect2)
                            width_start = max(new_rect['bounds'][0] - text_width, 0)
                            height_start = max(new_rect['bounds'][1] - text_height, 0)
                            new_rect['id_bounds'] = [width_start, height_start, width_start + text_width, height_start + text_height]
                            next_id += 1
                            new_rects.append(new_rect)
                            skip_indices.update([rect1['id'], rect2['id']])
                            merged = True
                            break
                if rect1['id'] not in skip_indices:
                    new_rects.append(rect1)

            rects = new_rects

        return rects, next_id
