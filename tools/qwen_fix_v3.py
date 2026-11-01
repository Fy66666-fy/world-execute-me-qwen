# v3 修补：f_reach 左侧旧徽章蓝盘/蓝穗擦除为透明；boy/man 锥底蓝梢清除。
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage
from qwen_ornament import BLUE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")

def blueish(a):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (b - r > 40) & (b - g > 40)

def drop_small_blue(name, boxes, max_area):
    p = os.path.join(CHAR, f"{name}.png")
    im = Image.open(p).convert("RGBA"); a = np.array(im)
    al = a[:, :, 3] > 128
    blue = al & blueish(a)
    lab, n = ndimage.label(blue)
    sizes = ndimage.sum(blue, lab, range(1, n + 1))
    zb = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in boxes: zb[y0:y1, x0:x1] = True
    gone = 0
    for i in range(1, n + 1):
        m = lab == i
        if sizes[i - 1] > max_area: continue
        if (m & zb).any():
            a[m, 3] = 0; gone += int(sizes[i - 1])
    Image.fromarray(a, "RGBA").save(p)
    print(name, "erased", gone, "px")

def clear_box(name, box):
    p = os.path.join(CHAR, f"{name}.png")
    im = Image.open(p).convert("RGBA"); a = np.array(im)
    x0, y0, x1, y1 = box
    a[y0:y1, x0:x1, 3] = 0
    Image.fromarray(a, "RGBA").save(p)
    print(name, "cleared", box)

# f_reach：旧徽章盘 + 旧垂穗（都是小块蓝，主发块很大要保留）
drop_small_blue("f_reach", [(190, 40, 350, 210), (210, 160, 350, 490)], 40000)
# boy / man：锥底下方的蓝梢（该处背景为空）
clear_box("boy_bust", (690, 680, 900, 760))
clear_box("man_bust", (668, 662, 878, 742))
