# 四张 Claude 底图终版重做：从备份出发（橙→蓝），花盘大半径整体涂蓝埋掉，
# 缎带组件：头发轮廓内→涂蓝，轮廓外→擦透；再画发丝+米白徽章+锥形流苏。
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from qwen_ornament import BLUE, CREAM, BLACK, SS, ORANGE, draw_mark

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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
BAK = os.path.join(ROOT, "backup_pre_ornament")

def blueish(a):
    r, g, b = a[:, :, 0].astype(int), a[:, :, 1].astype(int), a[:, :, 2].astype(int)
    return (b - r > 40) & (b - g > 40)

def recolor(a):
    rgb = a[:, :, :3].astype(int)
    do = ((rgb - np.array(ORANGE))**2).sum(2)
    dn = ((rgb - np.array(BLUE))**2).sum(2); dc = ((rgb - np.array(CREAM))**2).sum(2); db = ((rgb - np.array(BLACK))**2).sum(2)
    m = (do < 120**2) & (do < dn) & (do < dc) & (do < db)
    a[m, 0], a[m, 1], a[m, 2] = BLUE

def hair_dilated(a, it=4):
    bl = (a[:, :, 3] > 128) & blueish(a)
    lab, n = ndimage.label(bl)
    sz = ndimage.sum(bl, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sz)) + 1)
    return ndimage.binary_dilation(main, np.ones((9, 9)), iterations=it)

for name, fx, fy, R, ribbon_box in [
    ("cat_bust",  790, 269, 96, (690, 330, 900, 640)),
    ("cat_paws",  801, 263, 96, (700, 325, 915, 635)),
    ("f_profile", 704, 252, 92, (610, 315, 820, 620)),
    ("f_eye",     978, 285, 150, (870, 380, 1120, 760)),
]:
    a = np.array(Image.open(os.path.join(BAK, f"{name}.png")).convert("RGBA"))
    recolor(a)
    al = a[:, :, 3] > 128
    ink = al & ~blueish(a)                      # 米白/黑/杂色 = 旧花+缎带+脸/衣
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    # ① 花盘整体（含尖端）：圆内非蓝墨色 → 涂蓝
    circ = (xx - fx)**2 + (yy - fy)**2 < (R * 1.75)**2
    a[ink & circ, 0], a[ink & circ, 1], a[ink & circ, 2] = BLUE
    # ② 缎带框内剩余组件：头发轮廓内→涂蓝，外→擦透（脸/衣在框外，不受影响）
    ink2 = (a[:, :, 3] > 128) & ~blueish(a)
    x0, y0, x1, y1 = ribbon_box
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    hd = hair_dilated(a)
    lab, n = ndimage.label(ink2 & zb)
    painted = wiped = 0
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 60: continue
        inp, outp = m & hd, m & ~hd
        a[inp, 0], a[inp, 1], a[inp, 2] = BLUE; painted += int(inp.sum())
        a[outp, 3] = 0; wiped += int(outp.sum())
    im = Image.fromarray(a, "RGBA")
    big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    strand(dr, (fx-30)*SS, (fy-R)*SS, (fx+40)*SS, (fy+R*1.6)*SS, -70*SS, 26*SS, 8*SS, BLACK)
    strand(dr, (fx+70)*SS, (fy-R*0.8)*SS, (fx+130)*SS, (fy+R*1.9)*SS, 60*SS, 20*SS, 6*SS, BLACK)
    draw_mark(dr, fx*SS, fy*SS, R*0.96*SS, CREAM)
    cone_tassel(dr, (fx+.06*R)*SS, (fy+1.05*R)*SS, R*.9*SS)
    big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, f"{name}.png"))
    print(name, "painted", painted, "wiped", wiped)
