from typing import List


class Rect:
    @staticmethod
    def is_nearby(rect1: List, rect2: List, dist: int) -> bool:
        """
        判断两个矩形是否相邻dist
        """
        mid_x1, mid_y1 = (rect1[0] + rect1[2]) / 2, (rect1[1] + rect1[3]) / 2
        w1, h1 = rect1[2] - rect1[0], rect1[3] - rect1[1]
        mid_x2, mid_y2 = (rect2[0] + rect2[2]) / 2, (rect2[1] + rect2[3]) / 2
        w2, h2 = rect2[2] - rect2[0], rect2[3] - rect2[1]

        if abs(mid_x1 - mid_x2) < (w1 / 2 + w2 / 2 + dist) and abs(mid_y1 - mid_y2) < (h1 / 2 + h2 / 2 + dist):
            return True
        return False

    @staticmethod
    def is_overlap(rect1: List, rect2: List) -> bool:
        """
        仅在相交但是不包含时返回True
        """
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        return x1 < x4 and y1 < y4 and x2 > x3 and y2 > y3 and not Rect.is_containing(rect1, rect2) and not Rect.is_containing(rect2, rect1)

    @staticmethod
    def is_containing(rect1: List, rect2: List) -> bool:
        """
        return bound1 是否被 bound2 包含
        """
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        return x1 >= x3 and y1 >= y3 and x2 <= x4 and y2 <= y4

    @staticmethod
    def iou_threshold(rect1: List, rect2: List, threshold: float) -> bool:
        """
        比较iou和threshold
        """
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        x5, y5, x6, y6 = max(x1, x3), max(y1, y3), min(x2, x4), min(y2, y4)
        if x5 >= x6 or y5 >= y6:
            iou = 0
        else:
            s1 = (x2 - x1) * (y2 - y1)
            s2 = (x4 - x3) * (y4 - y3)
            s3 = (x6 - x5) * (y6 - y5)
            iou = s3 / (s1 + s2 - s3)

        return iou > threshold

    @staticmethod
    def intersection_over_second_area(rect1: List, rect2: List) -> float:
        """
        返回 交集 / rect2面积
        """
        x_left = max(rect1[0], rect2[0])
        y_top = max(rect1[1], rect2[1])
        x_right = min(rect1[2], rect2[2])
        y_bottom = min(rect1[3], rect2[3])

        if x_right < x_left or y_bottom < y_top:
            return 0  # 没有相交区域

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        second_area = (rect2[2] - rect2[0]) * (rect2[3] - rect2[1])

        return intersection_area / second_area if second_area > 0.0 else 0.0

    @staticmethod
    def iou(bound1, bound2) -> float:
        x1, y1, x2, y2 = bound1
        x3, y3, x4, y4 = bound2
        x5, y5, x6, y6 = max(x1, x3), max(y1, y3), min(x2, x4), min(y2, y4)
        if x5 >= x6 or y5 >= y6:
            return 0
        else:
            s1 = (x2 - x1) * (y2 - y1)
            s2 = (x4 - x3) * (y4 - y3)
            s3 = (x6 - x5) * (y6 - y5)
            return s3 / (s1 + s2 - s3)
