# v4c：boy/man 恢复被 v3 误删的领结区；用"水平细条"检测删掉锥下的蓝色缎带尾巴；
#      f_reach 清白色残影 + 细条删蓝梢。
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
from scipy import ndimage
from qwen_ornament import BLUE, CREAM, BLACK, ORANGE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
BAK = os.path.join(ROOT, "backup_pre_ornament")

def blueish(a):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (b - r > 40) & (b - g > 40)

def recolor_orange(a):
    rgb = a[:, :, :3].astype(int)
    do = ((rgb - np.array(ORANGE))**2).sum(2)
    dn = ((rgb - np.array(BLUE))**2).sum(2); dc = ((rgb - np.array(CREAM))**2).sum(2); db = ((rgb - np.array(BLACK))**2).sum(2)
    m = (do < 120**2) & (do < dn) & (do < dc) & (do < db)
    a[m, 0], a[m, 1], a[m, 2] = BLUE
    return a

def thin_blue_runs(a, box, max_run=34):
    """box 内：蓝色像素的水平连续段长度 < max_run → 透明（缎带细条），宽发块保留。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    bl = (a[:, :, 3] > 128) & blueish(a)
    gone = 0
    for y in range(y0, y1):
        x = x0
        row = bl[y]
        while x < x1:
            if row[x]:
                x2 = x
                while x2 < x1 and row[x2]: x2 += 1
                if x2 - x < max_run:
                    a[y, x:x2, 3] = 0; gone += x2 - x
                x = x2
            else:
                x += 1
    return gone

def wipe_ghosts(a, box, max_area=8000, ink='cream'):
    """box 内小的 cream 连通块 → 透明（旧缎带白残影）。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    al = a[:, :, 3] > 128
    lum = a[:, :, :3].mean(2)
    m0 = al & (lum > 150) if ink == 'cream' else al & (lum < 90)
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    lab, n = ndimage.label(m0 & zb)
    sz = ndimage.sum(m0 & zb, lab, range(1, n + 1))
    gone = 0
    for i in range(1, n + 1):
        if sz[i - 1] <= max_area:
            m = lab == i; a[m, 3] = 0; gone += int(sz[i - 1])
    return gone

for name, restore_box, tail_box in [
    ("boy_bust", (690, 680, 900, 760), (676, 560, 930, 690)),
    ("man_bust", (668, 662, 878, 742), (654, 545, 908, 672)),
]:
    p = os.path.join(CHAR, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    b = np.array(Image.open(os.path.join(BAK, f"{name}.png")).convert("RGBA"))
    x0, y0, x1, y1 = restore_box
    a[y0:y1, x0:x1] = b[y0:y1, x0:x1]
    recolor_orange(a)
    # 恢复区里旧缎带的米白/黑条纹 → 透明（只删恢复盒内的中小块）
    g1 = wipe_ghosts(a, restore_box, max_area=15000, ink='cream')
    g2 = wipe_ghosts(a, restore_box, max_area=15000, ink='black')
    # 锥下的蓝缎带细条 → 透明
    g3 = thin_blue_runs(a, tail_box, max_run=34)
    Image.fromarray(a, "RGBA").save(p)
    print(name, "restored; wiped cream", g1, "black", g2, "thin-blue", g3)

# ---- f_reach -------------------------------------------------------------
p = os.path.join(CHAR, "f_reach.png")
a = np.array(Image.open(p).convert("RGBA"))
g1 = wipe_ghosts(a, (190, 60, 345, 480), max_area=8000, ink='cream')
g2 = thin_blue_runs(a, (312, 280, 432, 380), max_run=30)
Image.fromarray(a, "RGBA").save(p)
print("f_reach ghost", g1, "thin-blue", g2)
