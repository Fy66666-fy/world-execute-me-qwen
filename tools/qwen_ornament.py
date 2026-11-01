# Qwen 版人物素材就地编辑（只动 assets/character/*.png，不动任何代码）：
#  1) 橙发 → 千问蓝紫
#  2) 太阳花发饰 → 千问三瓣标志（官方 wordmark 路径）
#  3) 条纹缎带 → 流苏（帽坠结 + 横箍 + 相间垂穗）
#  4) f_bust / f_reach 的帽徽 → 米白圆片 + 黑色千问标志
import os, re, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
CREAM, BLUE, BLACK = (244, 224, 198), (72, 82, 196), (36, 26, 21)
ORANGE = (220, 114, 63)
SS = 4

BLADES = [
 'M16.4317 2.35157H11.5088C11.5088 2.14167 11.453 1.93176 11.3448 1.74482L10.6855 0.60346C10.4691 0.229567 10.0689 -0.0032959 9.63601 -0.0032959H8.31755C7.88462 -0.0032959 7.48449 0.226288 7.26803 0.60346L5.25097 4.09641C5.03451 4.4703 5.03451 4.93275 5.25097 5.30664L5.9102 6.448C6.12667 6.82189 6.5268 7.05476 6.95973 7.05476H16.4284C16.8613 7.05476 17.2615 6.82517 17.4779 6.448L18.1372 5.30664C18.3536 4.93275 18.3536 4.4703 18.1372 4.09641L17.4779 2.95505C17.2615 2.58116 16.8613 2.34829 16.4284 2.34829L16.4317 2.35157Z',
 'M13.4077 19.3932L15.8675 15.1295C16.0479 15.2345 16.2578 15.2935 16.4743 15.2935H17.7927C18.2257 15.2935 18.6258 15.0639 18.8423 14.6868L19.5015 13.5454C19.718 13.1715 19.718 12.7091 19.5015 12.3352L17.4844 8.84223C17.268 8.46834 16.8678 8.23547 16.4349 8.23547H15.1164C14.6835 8.23547 14.2834 8.46506 14.0669 8.84223L9.33422 17.0416C9.11776 17.4155 9.11776 17.878 9.33422 18.2519L9.99346 19.3932C10.2099 19.7671 10.6101 20 11.043 20H12.3614C12.7944 20 13.1945 19.7704 13.411 19.3932H13.4077Z',
 'M0.164057 8.25187L2.62388 12.5156C2.44349 12.6205 2.28934 12.7714 2.18111 12.9583L1.52188 14.0997C1.30542 14.4736 1.30542 14.936 1.52188 15.3099L2.18111 16.4513C2.39758 16.8252 2.79771 17.058 3.23064 17.058H7.26475C7.69767 17.058 8.09781 16.8284 8.31427 16.4513L8.9735 15.3099C9.18997 14.936 9.18997 14.4736 8.9735 14.0997L4.2408 5.90027C4.02434 5.52638 3.62421 5.29352 3.19128 5.29352H1.87281C1.43989 5.29352 1.03975 5.5231 0.82329 5.90027L0.164057 7.04163C-0.0524071 7.41553 -0.0524071 7.87797 0.164057 8.25187Z',
]
CX0, CY0, CR0 = 9.8328, 10.0, 10.3

def parse_path(d):
    toks = re.findall(r'[MLHVCSZ]|[-+]?\d*\.?\d+', d)
    pts, cur, start = [], [0.0, 0.0], [0.0, 0.0]
    i = 0
    while i < len(toks):
        c = toks[i]
        if not re.match(r'[MLHVCSZ]', c): i += 1; continue
        i += 1
        if c == 'M':
            cur = [float(toks[i]), float(toks[i+1])]; i += 2; start = list(cur); pts.append(tuple(cur))
        elif c == 'L':
            cur = [float(toks[i]), float(toks[i+1])]; i += 2; pts.append(tuple(cur))
        elif c == 'H':
            cur[0] = float(toks[i]); i += 1; pts.append(tuple(cur))
        elif c == 'C':
            p1 = [float(toks[i]), float(toks[i+1])]; p2 = [float(toks[i+2]), float(toks[i+3])]
            p3 = [float(toks[i+4]), float(toks[i+5])]; i += 6
            p0 = cur
            for k in range(1, 25):
                t = k / 24; mt = 1 - t
                pts.append((mt**3*p0[0] + 3*mt*mt*t*p1[0] + 3*mt*t*t*p2[0] + t**3*p3[0],
                            mt**3*p0[1] + 3*mt*mt*t*p1[1] + 3*mt*t*t*p2[1] + t**3*p3[1]))
            cur = p3
        elif c == 'Z':
            cur = list(start)
    return pts

BLADE_POLYS = [parse_path(d) for d in BLADES]

def draw_mark(dr, cx, cy, R, color, rot=0.0):
    s = R / CR0; a = np.radians(rot); ca, sa = np.cos(a), np.sin(a)
    for poly in BLADE_POLYS:
        dr.polygon([(cx + ((x-CX0)*s*ca - (y-CY0)*s*sa), cy + ((x-CX0)*s*sa + (y-CY0)*s*ca)) for x, y in poly], fill=color)

def strand(dr, x0, y0, x1, y1, bulge, w0, w1, color):
    ts = np.linspace(0, 1, 24)
    xs = (1-ts)**2*x0 + 2*(1-ts)*ts*(x0+bulge) + ts**2*x1
    ys = (1-ts)**2*y0 + 2*(1-ts)*ts*(y0+bulge*0.3) + ts**2*y1
    L, R = [], []
    for i in range(24):
        w = w0 + (w1-w0)*ts[i]
        dx = xs[min(i+1,23)]-xs[max(i-1,0)]; dy = ys[min(i+1,23)]-ys[max(i-1,0)]
        n = np.hypot(dx,dy) or 1
        L.append((xs[i]-dy/n*w/2, ys[i]+dx/n*w/2)); R.append((xs[i]+dy/n*w/2, ys[i]-dx/n*w/2))
    dr.polygon(L + R[::-1], fill=color)

def tassel(dr, x, y, R):
    """帽坠：圆结 + 横箍 + 7 根相间垂穗。坐标已是超采样单位。"""
    dr.ellipse([x-0.15*R, y-0.15*R, x+0.15*R, y+0.15*R], fill=BLACK)
    cw, ch = 1.02*R, 0.33*R
    dr.rounded_rectangle([x-cw/2, y, x+cw/2, y+ch], radius=ch*0.4, fill=BLACK)
    y0 = y + ch
    for i in range(7):
        f = (i-3)/3
        len_i = R * (2.5 + 0.55*np.cos(f*2.2))
        w = 0.22*R
        x0, x1 = x + f*0.42*cw, x + f*0.55*cw
        tip = (x0+x1)/2
        dr.polygon([(x0-w/2,y0),(x0+w/2,y0),(tip+w*0.16,y0+len_i),(tip-w*0.16,y0+len_i)], fill=CREAM if i%2==0 else BLACK)

REG = json.load(open(os.path.join(CHAR, "regions.json"), encoding="utf-8"))

def edit(name, orn_r, ribbon_box):
    p = os.path.join(CHAR, f"{name}.png")
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    rgb = a[:, :, :3].astype(int)
    do = ((rgb - np.array(ORANGE))**2).sum(2)
    dn = ((rgb - np.array(BLUE))**2).sum(2); dc = ((rgb - np.array(CREAM))**2).sum(2); db = ((rgb - np.array(BLACK))**2).sum(2)
    m = (do < 120**2) & (do < dn) & (do < dc) & (do < db)
    a[m, 0], a[m, 1], a[m, 2] = BLUE
    big = Image.fromarray(a, "RGBA").resize((im.width*SS, im.height*SS), Image.NEAREST)
    A = np.array(big)
    lum = A[:, :, :3].mean(2); al = A[:, :, 3] > 128
    ink = al & ((lum > 150) | (lum < 90))
    fx, fy = REG[name]["flower"][0], REG[name]["flower"][1]
    rx0, ry0, rx1, ry1 = [v*SS for v in ribbon_box]
    yy, xx = np.mgrid[0:A.shape[0], 0:A.shape[1]]
    zone = (np.hypot(xx-fx*SS, yy-(fy-6)*SS) < (orn_r+14)*SS) | ((xx>=rx0)&(xx<=rx1)&(yy>=ry0)&(yy<=ry1))
    lab, n = ndimage.label(ink)
    keep = np.zeros_like(ink)
    for i in range(1, n+1):
        mm = lab == i
        if mm.sum() < 400: continue
        if (mm & zone).sum() > 0.2*mm.sum(): keep |= mm
    keep = ndimage.binary_dilation(keep, np.ones((7,7)))
    A[keep, :3] = BLUE
    big = Image.fromarray(A, "RGBA")
    dr = ImageDraw.Draw(big)
    strand(dr, (fx-30)*SS, (fy-orn_r)*SS, (fx+40)*SS, (fy+orn_r*1.6)*SS, -70*SS, 26*SS, 8*SS, BLACK)
    strand(dr, (fx+70)*SS, (fy-orn_r*0.8)*SS, (fx+130)*SS, (fy+orn_r*1.9)*SS, 60*SS, 20*SS, 6*SS, BLACK)
    draw_mark(dr, fx*SS, fy*SS, orn_r*0.96*SS, CREAM)
    tassel(dr, fx*SS + orn_r*0.35*SS, fy*SS + orn_r*0.75*SS, orn_r*SS)
    big.resize(im.size, Image.LANCZOS).save(p)
    print("edited", name)

def badge(name, cx, cy, r):
    p = os.path.join(CHAR, f"{name}.png")
    im = Image.open(p).convert("RGBA")
    big = im.resize((im.width*SS, im.height*SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    dr.ellipse([(cx-r)*SS, (cy-r)*SS, (cx+r)*SS, (cy+r)*SS], fill=CREAM)
    draw_mark(dr, cx*SS, cy*SS, r*0.8*SS, BLACK)
    big.resize(im.size, Image.LANCZOS).save(p)
    print("badge", name)

if __name__ == "__main__":
    edit("cat_bust",  96, (700, 300, 1010, 700))
    edit("cat_paws",  96, (712, 295, 1020, 690))
    edit("f_profile", 92, (615, 285, 940, 660))
    edit("f_eye",    150, (900, 330, 1210, 790))
    edit("boy_bust",  88, (700, 300, 1000, 640))
    edit("man_bust",  88, (678, 282, 975, 620))
    badge("f_bust", 330, 300, 52)
    badge("f_reach", 280, 132, 46)
