# 终版：boy/man/f_bust/f_reach 从备份重做（组件法：轮廓内涂蓝、轮廓外擦透）；
#      cat_bust/cat_paws/f_profile/f_eye 只擦悬空蓝梢。
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from qwen_ornament import BLUE, CREAM, BLACK, SS, ORANGE, draw_mark

def cone_tassel(dr, x, y, R):
    """锥形帽坠：黑结 + 黑箍 + 米白扇形锥（黑线分缕、底缘圆头）。坐标=超采样单位。"""
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

def hair_dilated(a, it=6):
    bl = (a[:, :, 3] > 128) & blueish(a)
    lab, n = ndimage.label(bl)
    if n == 0: return bl
    sz = ndimage.sum(bl, lab, range(1, n + 1))
    main = lab == (int(np.argmax(sz)) + 1)
    return ndimage.binary_dilation(main, np.ones((9, 9)))

def fix_ornament(a, fx, fy, fr, ribbon_box):
    """花心圆内非蓝墨色→涂蓝；缎带框内组件：轮廓内涂蓝、轮廓外擦透。"""
    al = a[:, :, 3] > 128
    ink = al & ~blueish(a)
    yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    circ = (xx - fx)**2 + (yy - fy)**2 < (fr * 1.5)**2
    a[ink & circ, 0], a[ink & circ, 1], a[ink & circ, 2] = BLUE
    hd = hair_dilated(a)
    x0, y0, x1, y1 = ribbon_box
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    lab, n = ndimage.label(ink & zb)
    wiped = painted = 0
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 40 or m.sum() > 30000: continue
        inp = m & hd; outp = m & ~hd
        a[inp, 0], a[inp, 1], a[inp, 2] = BLUE; painted += int(inp.sum())
        a[outp, 3] = 0; wiped += int(outp.sum())
    return painted, wiped

# ---- 四张从备份重做 ------------------------------------------------------
JOBS = [
    # name, flower(cx,cy,r), ribbon_box, mark(cream at fx,fy,R) or badge(disk+black mark), tassel(x,y,R), strands?
    ("boy_bust",  (792, 267, 60), (700, 330, 880, 600), "mark", 88, True),
    ("man_bust",  (769, 249, 60), (676, 312, 856, 590), "mark", 88, True),
    ("f_bust",    (330, 300, 52), (250, 340, 430, 710), "badge", 52, False),
    ("f_reach",   (280, 132, 46), (225, 170, 340, 470), "badge", 46, False),
]
for name, (fx, fy, fr), box, kind, R, strands in JOBS:
    a = np.array(Image.open(os.path.join(BAK, f"{name}.png")).convert("RGBA"))
    recolor(a)
    p, w = fix_ornament(a, fx, fy, fr, box)
    im = Image.fromarray(a, "RGBA")
    big = im.resize((im.width * SS, im.height * SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    if strands:
        strand(dr, (fx-30)*SS, (fy-R)*SS, (fx+40)*SS, (fy+R*1.6)*SS, -70*SS, 26*SS, 8*SS, BLACK)
        strand(dr, (fx+70)*SS, (fy-R*0.8)*SS, (fx+130)*SS, (fy+R*1.9)*SS, 60*SS, 20*SS, 6*SS, BLACK)
        draw_mark(dr, fx*SS, fy*SS, R*0.96*SS, CREAM)
        cone_tassel(dr, (fx+.06*R)*SS, (fy+1.02*R)*SS, R*.9*SS)
    else:
        bx, by = (330, 300) if name == "f_bust" else (368, 108)
        dr.ellipse([(bx-R)*SS, (by-R)*SS, (bx+R)*SS, (by+R)*SS], fill=CREAM)
        draw_mark(dr, bx*SS, by*SS, R*0.8*SS, BLACK)
        cone_tassel(dr, (bx+0.06*R)*SS, (by+1.15*R)*SS, R*1.05*SS)
    big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, f"{name}.png"))
    print(name, "painted", p, "wiped", w)

# ---- 四张只擦悬空蓝梢 ----------------------------------------------------
for name, box in [("cat_bust", (700, 600, 920, 760)), ("cat_paws", (712, 595, 932, 755)),
                  ("f_profile", (615, 560, 830, 700)), ("f_eye", (880, 640, 1120, 820))]:
    p = os.path.join(CHAR, f"{name}.png")
    a = np.array(Image.open(p).convert("RGBA"))
    hd = hair_dilated(a)
    bl = (a[:, :, 3] > 128) & blueish(a)
    x0, y0, x1, y1 = box
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    lab, n = ndimage.label(bl & zb)
    gone = 0
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() > 40 and not (m & hd).any():
            a[m, 3] = 0; gone += int(m.sum())
    Image.fromarray(a, "RGBA").save(p)
    print(name, "stray blue gone", gone)

# f_reach 徽章标注更新
rp = os.path.join(CHAR, "regions.json")
reg = json.load(open(rp, encoding="utf-8"))
reg["f_reach"]["flower"] = [368, 108, 46]
json.dump(reg, open(rp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("regions updated")
