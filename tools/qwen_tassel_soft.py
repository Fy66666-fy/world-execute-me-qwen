# 六张 Claude 底图：擦掉几何流苏 → 重绘柔和丝线流苏（结+小箍+13根微弯散开的丝线+束腰）。
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from qwen_ornament import BLUE, CREAM, BLACK, SS, draw_mark

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")

def blueish(a):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (b - r > 40) & (b - g > 40)

def soft_tassel(dr, x, y, R, seed=7):
    """柔和丝线流苏：黑结 + 小箍 + 13 根微弯散开的米白丝线 + 束腰黑带。坐标=超采样单位。"""
    rng = np.random.default_rng(seed)
    dr.ellipse([x - .12*R, y - .12*R, x + .12*R, y + .12*R], fill=BLACK)
    dr.rounded_rectangle([x - .26*R, y + .08*R, x + .26*R, y + .38*R], radius=.13*R, fill=BLACK)
    y1 = y + .38*R
    sw = max(1, round(.042*R))
    for i in range(13):
        t = i / 12
        x0 = (t - .5) * .40
        xw = (t - .5) * .66
        xe = (t - .5) * 1.62 + rng.uniform(-.05, .05)
        L = (2.75 + .55 * np.cos((t - .5) * 3.0)) * R + rng.uniform(-.16, .16) * R
        pts = []
        for s in np.linspace(0, 1, 26):
            yy = y1 + s * L
            if s < .3:
                xo = x0 + (xw - x0) * (s / .3)
            else:
                f = (s - .3) / .7
                xo = xw + (xe - xw) * (f * f * (3 - 2 * f))          # smoothstep 散开
            wob = .045 * R * np.sin(s * 7 + i * 1.9) * max(0, s - .3)
            pts.append((x + xo * R + wob, yy))
        dr.line(pts, fill=CREAM, width=sw, joint="curve")
    yb = y1 + .30 * R
    dr.rounded_rectangle([x - .34*R, yb - .05*R, x + .34*R, yb + .07*R], radius=.05*R, fill=BLACK)

SEEDS = {"cat_bust": 11, "cat_paws": 23, "f_profile": 37, "f_eye": 51, "boy_bust": 67, "man_bust": 83}
REG = json.load(open(os.path.join(CHAR, "regions.json"), encoding="utf-8"))
for name in ["cat_bust", "cat_paws", "f_profile", "f_eye", "boy_bust", "man_bust"]:
    fx, fy, fr = REG[name]["flower"]
    R = fr if fr > 50 else 90
    p = os.path.join(CHAR, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    # ① 擦旧流苏：徽章下方区域（y > fy+0.9R，x ±1.2R）的米白/黑 → 涂蓝
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    al = a[:, :, 3] > 128
    lum = a[:, :, :3].mean(2)
    ink = al & ~blueish(a) & ((lum > 150) | (lum < 90))
    zone = (yy > fy + .95*R) & (yy < fy + 4.6*R) & (xx > fx - 1.2*R) & (xx < fx + 1.3*R)
    a[ink & zone, 0], a[ink & zone, 1], a[ink & zone, 2] = BLUE
    # ② 重绘柔和流苏（挂在徽章右下）
    im = Image.fromarray(a, "RGBA")
    big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    soft_tassel(dr, (fx + .05*R)*SS, (fy + .80*R)*SS, .92*R*SS, seed=SEEDS[name])
    big.resize(im.size, Image.LANCZOS).save(p)
    print(name, "tassel softened")
