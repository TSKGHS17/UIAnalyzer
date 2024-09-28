import subprocess
import platform
from typing import Dict, Tuple, List
from PIL import Image


RED = '\033[91m'
BLUE = '\033[94m'
GREEN = '\033[32m'
END = '\033[0m'


def exec_command(c: str, timeout: int = 10) -> Dict:
    """
    :param c: command to execute
    :param timeout: timeout in seconds
    :return: command execute result
    """
    ret = {
        'code': 0,
        'message': ''
    }

    if platform.system() == "Windows":
        shell = ['cmd', '/c']
    else:
        shell = ['/bin/sh', '-c']

    try:
        out = subprocess.check_output(shell + [c], timeout=timeout, stderr=subprocess.STDOUT)
        ret['message'] = out.decode('utf-8')
        return ret
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print(f"Output: {e.output.decode('utf-8')}")
        raise
    except Exception as e:
        print(RED + "The command is: " + c + ", and the result is: " + repr(e) + END)
        raise


def get_bounds_average_color(image_path: str, bounds: List) -> Tuple[int, int, int]:
    """获得边框的平均颜色"""
    image = Image.open(image_path)
    w, h = image.size[0], image.size[1]
    pixels = image.load()
    r, g, b = 0, 0, 0
    count = 0

    for x in range(bounds[0], min(bounds[2], w)):
        for y in [bounds[1], min(bounds[3]-1, h-1)]:  # 只取边框的上下边界像素
            r += pixels[x, y][0]
            g += pixels[x, y][1]
            b += pixels[x, y][2]
            count += 1

    for y in range(bounds[1], min(bounds[3], h)):
        for x in [bounds[0], min(bounds[2] - 1, w-1)]:  # 只取边框的左右边界像素
            r += pixels[x, y][0]
            g += pixels[x, y][1]
            b += pixels[x, y][2]
            count += 1

    return r // count, g // count, b // count


def get_inverse_color(avg_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """获得反色"""
    inverse_color = (255 - avg_color[0], 255 - avg_color[1], 255 - avg_color[2])
    return inverse_color
