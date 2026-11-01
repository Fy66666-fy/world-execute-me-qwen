# 收尾：① 头发轮廓内的透明洞 → 填蓝发 ② 按精确框擦掉缎带残片（避开流苏/衣领/脸）
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

# name -> 缎带残片框（x0,y0,x1,y1），已按组件坐标避开流苏与衣领
BOXES = {
    "cat_bust":  [(885, 400, 995, 715), (845, 630, 880, 700)],
    "cat_paws":  [(905, 395, 1015, 680), (856, 630, 878, 692)],
    "f_profile": [(795, 320, 995, 690), (870, 770, 975, 890)],
    "f_eye":     [(1030, 640, 1180, 1010), (1150, 920, 1190, 1030)],
    "boy_bust":  [(860, 380, 990, 620)],
    "man_bust":  [(838, 362, 968, 600)],
}

for name, boxes in BOXES.items():
    p = os.path.join(CHAR, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    al = a[:, :, 3] > 128
    bl = al & blueish(a)
    lab, n = ndimage.label(bl)
    if n:
        sz = ndimage.sum(bl, lab, range(1, n + 1))
        main = lab == (int(np.argmax(sz)) + 1)
        holes = ndimage.binary_fill_holes(ndimage.binary_closing(main, np.ones((15, 15)))) & ~al
        # 只填小洞（<40k），大洞是真实背景
        hl, hn = ndimage.label(holes)
        hs = ndimage.sum(holes, hl, range(1, hn + 1))
        filled = 0
        for i in range(1, hn + 1):
            if hs[i - 1] <= 40000:
                m = hl == i
                a[m, 0], a[m, 1], a[m, 2] = BLUE
                a[m, 3] = 255
                filled += int(hs[i - 1])
    else:
        filled = 0
    # 擦残片：框内非蓝墨色 → 透明
    lum = a[:, :, :3].mean(2)
    ink = (a[:, :, 3] > 128) & ~blueish(a) & ((lum > 150) | (lum < 90))
    wiped = 0
    for x0, y0, x1, y1 in boxes:
        zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
        m = ink & zb
        a[m, 3] = 0; wiped += int(m.sum())
    Image.fromarray(a, "RGBA").save(p)
    print(name, "holes filled", filled, "ribbon wiped", wiped)
