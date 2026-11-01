# v2：流苏改锥形（参考千问大小姐身上那种帽坠穗），并修正 f_reach 徽章位置。
# 只改 assets/character/*.png 与 f_reach 的 regions 标注。
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from qwen_ornament import CREAM, BLUE, BLACK, SS, draw_mark

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")

def cone_tassel(dr, x, y, R):
    """锥形帽坠：黑结 + 黑箍 + 米白扇形锥（黑线分缕、底缘圆头），坐标=超采样单位。"""
    dr.ellipse([x - .15*R, y - .15*R, x + .15*R, y + .15*R], fill=BLACK)
    dr.rounded_rectangle([x - .45*R, y + .08*R, x + .45*R, y + .34*R], radius=.12*R, fill=BLACK)
    y1, y2 = y + .34*R, y + 2.9*R
    tw, bw = .62*R, 1.55*R
    dr.polygon([(x-tw/2, y1), (x+tw/2, y1), (x+bw/2, y2), (x-bw/2, y2)], fill=CREAM)
    n = 8
    for i in range(n):
        xb = x - bw/2 + (i+1)*bw/(n+1)
        xt = x - tw/2 + (i+1)*tw/(n+1)
        dr.line([xt, y1+.08*R, xb, y2], fill=BLACK, width=max(1, round(.05*R)))
    r = bw/(2*(n+1))
    for i in range(n+1):
        cx = x - bw/2 + i*bw/n
        dr.ellipse([cx-r, y2-r*0.8, cx+r, y2+r], fill=CREAM)

def wipe(a, box, keep=None):
    x0, y0, x1, y1 = [int(v) for v in box]
    lum = a[:, :, :3].mean(2); al = a[:, :, 3] > 128
    m = al & ((lum > 150) | (lum < 90))
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    m &= zb
    if keep is not None:
        kx, ky, kr = keep
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        m &= ~((xx-kx)**2 + (yy-ky)**2 < kr*kr)
    a[m, 0], a[m, 1], a[m, 2] = BLUE
    return int(m.sum())

def load(name):
    p = os.path.join(CHAR, f"{name}.png")
    return p, Image.open(p).convert("RGBA")

def save(p, im, big):
    big.resize(im.size, Image.LANCZOS).save(p)

REG = os.path.join(CHAR, "regions.json")
regions = json.load(open(REG, encoding="utf-8"))

# ---- 六张 Claude 底图：擦旧流苏 → 画锥形 -------------------------------
CLAUDE = {  # name: (fx, fy, orn_r)
 "cat_bust": (790, 269, 96), "cat_paws": (801, 263, 96), "f_profile": (704, 252, 92),
 "f_eye": (978, 285, 150), "boy_bust": (792, 267, 88), "man_bust": (769, 249, 88),
}
for name, (fx, fy, R) in CLAUDE.items():
    p, im = load(name); a = np.array(im)
    ax, ay = fx + .35*R, fy + .75*R
    wiped = wipe(a, (ax-1.0*R, fy+.52*R, ax+1.0*R, fy+4.3*R), keep=(fx, fy, 1.0*R))
    big = Image.fromarray(a, "RGBA").resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    cone_tassel(dr, (fx+.06*R)*SS, (fy+1.02*R)*SS, R*.9*SS)
    save(p, im, big); print(name, "wiped", wiped)

# ---- f_bust：擦旧流苏（护住圆徽）→ 画锥形 ------------------------------
p, im = load("f_bust"); a = np.array(im)
wiped = wipe(a, (274, 333, 422, 615), keep=(330, 300, 58))
big = Image.fromarray(a, "RGBA").resize((im.width*SS, im.height*SS), Image.NEAREST)
dr = ImageDraw.Draw(big)
cone_tassel(dr, 345*SS, 352*SS, 70*SS)
save(p, im, big); print("f_bust wiped", wiped)

# ---- f_reach：擦错位的圆徽+残留缎带/旋纹 → 帽冠正中重画 → 锥形流苏 -------
p, im = load("f_reach"); a = np.array(im)
w1 = wipe(a, (226, 78, 338, 184))      # 旧圆徽
w2 = wipe(a, (234, 176, 332, 474))      # 旧缎带/流苏
w3 = wipe(a, (330, 64, 428, 142))       # 原图旋纹残留
big = Image.fromarray(a, "RGBA").resize((im.width*SS, im.height*SS), Image.NEAREST)
dr = ImageDraw.Draw(big)
dr.ellipse([(368-46)*SS, (108-46)*SS, (368+46)*SS, (108+46)*SS], fill=CREAM)
draw_mark(dr, 368*SS, 108*SS, 46*.8*SS, BLACK)
cone_tassel(dr, 372*SS, 150*SS, 56*SS)
save(p, im, big); print("f_reach wiped", w1, w2, w3)
regions["f_reach"]["flower"] = [368, 108, 46]
json.dump(regions, open(REG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
