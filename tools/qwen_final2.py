# 最终清理（六张 Claude 底图）：
#  ① 花心环带 [1.05R, 2.6R] 内所有非蓝墨色 → 涂蓝（埋掉旧太阳花尖瓣）
#  ② 缎带框内所有米白/黑墨色 → 擦透明（去残片与虚线）
#  ③ 填小洞  ④ 重画发丝 + 米白徽章 + 锥形流苏
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from qwen_ornament import BLUE, CREAM, BLACK, SS, draw_mark

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")

def cone_tassel(dr, x, y, R):
    dr.ellipse([x - .15*R, y - .15*R, x + .15*R, y + .15*R], fill=BLACK)
    dr.rounded_rectangle([x - .45*R, y + .08*R, x + .45*R, y + .34*R], radius=.12*R, fill=BLACK)
    y1, y2 = y + .34*R, y + 2.9*R
    tw, bw = .62*R, 1.55*R
    dr.polygon([(x-tw/2, y1), (x+tw/2, y1), (x+bw/2, y2), (x-bw/2, y2)], fill=CREAM)
    n = 8
    for i in range(n):
        xb = x - bw/2 + (i+1)*bw/(n+1); xt = x - tw/2 + (i+1)*tw/(n+1)
        dr.line([xt, y1+.08*R, xb, y2], fill=BLACK, width=max(1, round(.05*R)))
    r = bw/(2*(n+1))
    for i in range(n+1):
        cx = x - bw/2 + i*bw/n
        dr.ellipse([cx-r, y2-r*0.8, cx+r, y2+r], fill=CREAM)

def strand(dr, x0, y0, x1, y1, bulge, w0, w1, color):
    ts = np.linspace(0, 1, 24)
    xs = (1-ts)**2*x0 + 2*(1-ts)*ts*(x0+bulge) + ts**2*x1
    ys = (1-ts)**2*y0 + 2*(1-ts)*ts*(y0+bulge*0.3) + ts**2*y1
    L, R = [], []
    for i in range(24):
        w = w0 + (w1-w0)*ts[i]
        dx = xs[min(i+1,23)]-xs[max(i-1,0)]; dy = ys[min(i+1,23)]-ys[max(i-1,0)]
        nrm = np.hypot(dx,dy) or 1
        L.append((xs[i]-dy/nrm*w/2, ys[i]+dx/nrm*w/2)); R.append((xs[i]+dy/nrm*w/2, ys[i]-dx/nrm*w/2))
    dr.polygon(L + R[::-1], fill=color)

def blueish(a):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (b - r > 40) & (b - g > 40)

JOBS = [
    # name, fx, fy, R, ring_outer, ribbon_boxes
    ("cat_bust",  790, 269, 96, 2.6, [(830, 300, 1010, 640)]),
    ("cat_paws",  801, 263, 96, 2.6, [(845, 295, 1025, 635)]),
    ("f_profile", 704, 252, 92, 2.6, [(790, 285, 1000, 700)]),
    ("f_eye",     978, 285, 150, 2.3, [(1075, 360, 1254, 800)]),
    ("boy_bust",  792, 267, 88, 2.6, [(845, 320, 1010, 620)]),
    ("man_bust",  769, 249, 88, 2.6, [(820, 305, 985, 600)]),
]
for name, fx, fy, R, ring, boxes in JOBS:
    p = os.path.join(CHAR, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    al = a[:, :, 3] > 128
    ink = al & ~blueish(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    d = np.sqrt((xx - fx)**2 + (yy - fy)**2)
    ringm = ink & (d > R * 1.05) & (d < R * ring)
    a[ringm, 0], a[ringm, 1], a[ringm, 2] = BLUE
    wiped = 0
    for x0, y0, x1, y1 in boxes:
        zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
        m = ink & zb
        a[m, 3] = 0; wiped += int(m.sum())
    # 填小洞
    bl = (a[:, :, 3] > 128) & blueish(a)
    lab, n = ndimage.label(bl)
    if n:
        sz = ndimage.sum(bl, lab, range(1, n + 1))
        main = lab == (int(np.argmax(sz)) + 1)
        holes = ndimage.binary_fill_holes(ndimage.binary_closing(main, np.ones((15, 15)))) & ~(a[:, :, 3] > 128)
        hl, hn = ndimage.label(holes)
        hs = ndimage.sum(holes, hl, range(1, hn + 1))
        for i in range(1, hn + 1):
            if hs[i - 1] <= 40000:
                m = hl == i
                a[m, 0], a[m, 1], a[m, 2] = BLUE; a[m, 3] = 255
    im = Image.fromarray(a, "RGBA")
    big = im.resize((im.width * SS, im.height * SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    strand(dr, (fx - 30) * SS, (fy - R) * SS, (fx + 40) * SS, (fy + R * 1.6) * SS, -70 * SS, 26 * SS, 8 * SS, BLACK)
    strand(dr, (fx + 70) * SS, (fy - R * 0.8) * SS, (fx + 130) * SS, (fy + R * 1.9) * SS, 60 * SS, 20 * SS, 6 * SS, BLACK)
    draw_mark(dr, fx * SS, fy * SS, R * 0.96 * SS, CREAM)
    cone_tassel(dr, (fx + .06 * R) * SS, (fy + 1.05 * R) * SS, R * .9 * SS)
    big.resize(im.size, Image.LANCZOS).save(p)
    print(name, "ring", int(ringm.sum()), "wiped", wiped)
