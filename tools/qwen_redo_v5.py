# v5 最终重做（从 backup_pre_ornament 出发，一次成型）：
#  boy/man：① 旧太阳花圆盘 → 涂蓝埋进头发 ② 缎带（悬在空白区的米白/黑条）→ 擦透明
#           ③ 重画发丝两缕 + 米白千问徽章 + 锥形流苏
#  f_reach：① 帽左侧旧缎带（米白/黑）→ 擦透明 ② 帽冠正中米白徽章 + 锥穗
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from qwen_ornament import BLUE, CREAM, BLACK, SS, ORANGE, draw_mark
from qwen_redo import cone_tassel, strand

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
BAK = os.path.join(ROOT, "backup_pre_ornament")

def recolor(a):
    rgb = a[:, :, :3].astype(int)
    do = ((rgb - np.array(ORANGE))**2).sum(2)
    dn = ((rgb - np.array(BLUE))**2).sum(2); dc = ((rgb - np.array(CREAM))**2).sum(2); db = ((rgb - np.array(BLACK))**2).sum(2)
    m = (do < 120**2) & (do < dn) & (do < dc) & (do < db)
    a[m, 0], a[m, 1], a[m, 2] = BLUE

def paint_circle_blue(a, cx, cy, r):
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    m = (a[:, :, 3] > 128) & ((xx-cx)**2 + (yy-cy)**2 < r*r)
    a[m, 0], a[m, 1], a[m, 2] = BLUE
    return int(m.sum())

def wipe_ink_box(a, box):
    """box 内米白/黑（含其抗锯齿边）→ 透明。"""
    x0, y0, x1, y1 = [int(v) for v in box]
    al = a[:, :, 3] > 128
    lum = a[:, :, :3].mean(2)
    m = np.zeros_like(al); m[y0:y1, x0:x1] = al[y0:y1, x0:x1] & ((lum[y0:y1, x0:x1] > 150) | (lum[y0:y1, x0:x1] < 90))
    a[m, 3] = 0
    return int(m.sum())

for name, fx, fy, R, ribbon in [
    ("boy_bust", 792, 267, 88, (688, 300, 962, 655)),
    ("man_bust", 769, 249, 88, (665, 282, 936, 636)),
]:
    p = os.path.join(BAK, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    recolor(a)
    g1 = paint_circle_blue(a, fx, fy - 4, R * 1.32)      # 埋掉旧太阳花
    g2 = wipe_ink_box(a, ribbon)                          # 擦掉旧缎带
    im = Image.fromarray(a, "RGBA")
    big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    strand(dr, (fx-30)*SS, (fy-R)*SS, (fx+40)*SS, (fy+R*1.6)*SS, -70*SS, 26*SS, 8*SS, BLACK)
    strand(dr, (fx+70)*SS, (fy-R*0.8)*SS, (fx+130)*SS, (fy+R*1.9)*SS, 60*SS, 20*SS, 6*SS, BLACK)
    draw_mark(dr, fx*SS, fy*SS, R*0.96*SS, CREAM)
    cone_tassel(dr, (fx+.06*R)*SS, (fy+1.02*R)*SS, R*.9*SS)
    big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, f"{name}.png"))
    print(name, "flower buried", g1, "ribbon wiped", g2)

# ---- f_reach -------------------------------------------------------------
a = np.array(Image.open(os.path.join(BAK, "f_reach.png")).convert("RGBA"))
g = wipe_ink_box(a, (196, 44, 332, 272))                  # 帽左侧旧缎带
im = Image.fromarray(a, "RGBA")
big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
dr = ImageDraw.Draw(big)
dr.ellipse([(368-46)*SS, (108-46)*SS, (368+46)*SS, (108+46)*SS], fill=CREAM)
draw_mark(dr, 368*SS, 108*SS, 46*.8*SS, BLACK)
cone_tassel(dr, 372*SS, 150*SS, 56*SS)
big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, "f_reach.png"))
print("f_reach ribbon wiped", g)
