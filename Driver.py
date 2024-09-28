import time
import platform
from typing import Dict, Tuple
import re

from Utils import exec_command, RED, END


class Driver:
    def __init__(self, device_id=0) -> None:
        super().__init__()
        self.width = None
        self.height = None

    # 获取屏幕尺寸
    def get_device_size(self) -> Tuple:
        c = f'adb shell wm size'
        size = exec_command(c)['message']
        override_match = re.search(r"Override size: (\d+x\d+)", size)
        physical_match = re.search(r"Physical size: (\d+x\d+)", size)
        if override_match:
            size_str = override_match.group(1)
        elif physical_match:
            size_str = physical_match.group(1)
        else:
            return
        
        self.width, self.height = map(int, size_str.split('x'))
        return self.width, self.height
    
    # 截屏
    def screenshot(self, save_path: str) -> str:
        c = f"adb shell screencap -p /sdcard/screenshot.png"
        exec_command(c)
        c = f"adb pull /sdcard/screenshot.png {save_path}"
        exec_command(c)
        return save_path

    # 返回
    def go_back(self) -> Dict:
        print(RED + "Go back to the previous page" + END)
        ret = exec_command("adb shell input keyevent 4")
        time.sleep(8)
        return ret

    # 点击
    def click(self, x: int, y: int) -> Dict:
        c = f"adb shell input tap {x} {y}"
        return exec_command(c)

    # 长按
    def long_click(self, x: int, y: int) -> Dict:
        c = f"adb shell input swipe {x} {y} {x} {y} {1500}"
        return exec_command(c)
    
    # 滑动
    def scroll(self, x1: int, y1: int, x2: int, y2: int, duration: int = 500) -> Dict:
        c = f"adb shell input swipe {x1} {y1} {x2} {y2} {duration}"
        return exec_command(c)
    
    # 输入
    def type(self, x: int, y: int, text: str) -> Dict:
        exec_command(f"adb shell input tap {x} {y}")
        time.sleep(5)
        return exec_command(f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{text}'")

    # 删除文本框的内容
    def delete_text(self, x: int, y: int, times=50) -> None:
        exec_command(f"adb shell input tap {x} {y}")
        for i in range(times):
            exec_command(f"adb shell input keyevent 67")
            exec_command(f"adb shell input keyevent 112")

    # 获取xml
    def get_xml(self, xml_path: str) -> Dict:
        """
        adb dump xml may get failed when parsing some activities
        """
        dev_null = 'nul' if platform.system() == "Windows" else '/dev/null'
        exec_command(f"adb shell uiautomator dump /sdcard/uidump.xml > {dev_null} 2>&1")
        time.sleep(1)
        ret = exec_command(f"adb pull /sdcard/uidump.xml {xml_path} > {dev_null} 2>&1")
        time.sleep(2)
        return ret
    