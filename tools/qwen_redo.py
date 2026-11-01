# 干净重做三张：boy_bust / man_bust / f_reach —— 从 backup_pre_ornament 出发，一次成型。
# 规则：只擦"缎带区内的小连通块（<80k px，≥30% 面积在区）"——米白/黑/蓝/白残影通吃；
#      头发、帽子、领结都是大连通块，天然受保护。然后重画米白千问徽章 + 锥形流苏。
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from qwen_ornament import BLUE, CREAM, BLACK, SS, ORANGE, draw_mark

def recolor(a):
    """橙色像素（含抗锯齿边）→ 蓝紫。"""
    rgb = a[:, :, :3].astype(int)
    do = ((rgb - np.array(ORANGE))**2).sum(2)
    dn = ((rgb - np.array(BLUE))**2).sum(2); dc = ((rgb - np.array(CREAM))**2).sum(2); db = ((rgb - np.array(BLACK))**2).sum(2)
    m = (do < 120**2) & (do < dn) & (do < dc) & (do < db)
    a[m, 0], a[m, 1], a[m, 2] = BLUE

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
BAK = os.path.join(ROOT, "backup_pre_ornament")

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

def wipe_zone(im, box, max_size=80000, frac=0.3):
    a = np.array(im); al = a[:, :, 3] > 128
    lab, n = ndimage.label(al)
    x0, y0, x1, y1 = [int(v) for v in box]
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    gone = 0
    for i in range(1, n+1):
        m = lab == i; s = int(m.sum())
        if s > max_size or s < 20: continue
        if (m & zb).sum() / s > frac:
            a[m, 3] = 0; gone += s
    return Image.fromarray(a, "RGBA"), gone

# ---- boy_bust / man_bust：备份 → 上蓝 → 擦缎带 → 徽章+锥穗+发丝 ----------
for name, (fx, fy, R), box in [
    ("boy_bust", (792, 267, 88), (660, 280, 1010, 720)),
    ("man_bust", (769, 249, 88), (640, 262, 985, 700)),
]:
    im = Image.open(os.path.join(BAK, f"{name}.png")).convert("RGBA")
    a = np.array(im); recolor(a)
    im = Image.fromarray(a, "RGBA")
    im, g = wipe_zone(im, box)
    big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    strand(dr, (fx-30)*SS, (fy-R)*SS, (fx+40)*SS, (fy+R*1.6)*SS, -70*SS, 26*SS, 8*SS, BLACK)
    strand(dr, (fx+70)*SS, (fy-R*0.8)*SS, (fx+130)*SS, (fy+R*1.9)*SS, 60*SS, 20*SS, 6*SS, BLACK)
    draw_mark(dr, fx*SS, fy*SS, R*0.96*SS, CREAM)
    cone_tassel(dr, (fx+.06*R)*SS, (fy+1.02*R)*SS, R*.9*SS)
    big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, f"{name}.png"))
    print(name, "wiped", g)

# ---- f_reach：备份（AIGC 千问娘，白条纹缎带在帽左侧）→ 擦缎带 → 帽冠正中徽章+锥穗 ----
im = Image.open(os.path.join(BAK, "f_reach.png")).convert("RGBA")
im, g = wipe_zone(im, (205, 40, 365, 480))
big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
dr = ImageDraw.Draw(big)
dr.ellipse([(368-46)*SS, (108-46)*SS, (368+46)*SS, (108+46)*SS], fill=CREAM)
draw_mark(dr, 368*SS, 108*SS, 46*.8*SS, BLACK)
cone_tassel(dr, 372*SS, 150*SS, 56*SS)
big.resize(im.size, Image.LANCZOS).save(os.path.join(CHAR, "f_reach.png"))
print("f_reach wiped", g)
