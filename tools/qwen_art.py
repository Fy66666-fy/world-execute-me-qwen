# Qwen 版素材处理：把 AIGC 三色立绘转成引擎可用的透明底剪影 PNG + regions.json 标注。
# 流程：1) 清右下角水印白字 2) 白底转透明 3) 量化到三色 4) 缩放对齐原版构图 5) 自动标注 face/chin/flower 等。
import json, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
# 原版三色（INK_RGB）：cream / orange(→蓝) / black
INKS = np.array([[244, 224, 198], [72, 82, 196], [36, 26, 21]], dtype=np.float64)
ORIG_W, ORIG_H = 1086, 1448

def clean_watermark(a):
    """右下角白字水印：在暗色裙摆上的孤立亮像素 → 填成周围暗色。"""
    H, W = a.shape[:2]
    lum = a.mean(2)
    y0, x0 = int(H * 0.90), int(W * 0.45)
    reg = a[y0:, x0:]
    rl = lum[y0:, x0:]
    mask = rl > 190
    # 只处理周围是暗色的亮像素（字），不碰真实白裙（白裙周围也是白/亮）
    from scipy import ndimage
    dark_neigh = ndimage.maximum_filter((rl < 120).astype(np.uint8), size=9) > 0
    hit = mask & dark_neigh
    lab, n = ndimage.label(hit)
    keep = np.zeros_like(hit)
    for i in range(1, n + 1):
        sz = int((lab == i).sum())
        if sz < 4000:  # 小连通块=字
            keep |= lab == i
    reg[keep] = [72, 82, 196]
    a[y0:, x0:] = reg
    return a

def to_rgba(a):
    lum = a.mean(2)
    alpha = np.where(lum > 235, 0, 255).astype(np.uint8)
    # 量化到三色
    flat = a.reshape(-1, 3).astype(np.float64)
    d = ((flat[:, None, :] - INKS[None, :, :]) ** 2).sum(2)
    q = d.argmin(1).reshape(a.shape[:2])
    out = INKS[q].astype(np.uint8)
    rgba = np.dstack([out, alpha])
    return rgba

def analyze(rgba, name):
    """自动标注：face=上半区亮块重心，chin=脸下缘，flower=头部右上的非蓝小连通块。"""
    lum = rgba[:, :, :3].mean(2)
    A = rgba[:, :, 3] > 128
    H, W = A.shape
    ys, xs = np.where(A)
    fig = [int(xs.min()), int(ys.min()), int((xs.max()-xs.min())), int((ys.max()-ys.min()))]
    # 脸：白色像素在 y < 45%H 的最大连通块
    from scipy import ndimage
    cream = A & (lum > 150)
    cream_top = cream.copy(); cream_top[int(H*0.5):, :] = False
    lab, n = ndimage.label(cream_top)
    face = [0, 0, 1, 1]; chin = [W//2, H//2]
    if n:
        sizes = ndimage.sum(cream_top, lab, range(1, n+1))
        big = (lab == (int(np.argmax(sizes)) + 1))
        ys2, xs2 = np.where(big)
        face = [int(xs2.min()), int(ys2.min()), int(xs2.max()-xs2.min()), int(ys2.max()-ys2.min())]
        chin = [int((xs2.min()+xs2.max())//2), int(ys2.max())]
    # flower/帽徽：头部区（y<30%H）非蓝非白的小块重心
    head = A.copy(); head[int(H*0.32):, :] = False
    blue = (rgba[:,:,2].astype(int) - rgba[:,:,0] > 30) & (lum > 60) & (lum < 200)
    dark = (lum <= 60) & head
    if dark.sum() > 200:
        ys3, xs3 = np.where(dark)
        flower = [int(xs3.mean()), int(ys3.mean()), 60]
    else:
        flower = [face[0]+face[2]//2, max(10, face[1]), 60]
    return {"figure": fig, "face": face, "chin": chin, "flower": flower, "size": [W, H]}

def main():
    from scipy import ndimage  # noqa
    srcs = {
        "f_bust":  sys.argv[1] if len(sys.argv) > 1 else None,
        "f_reach": sys.argv[2] if len(sys.argv) > 2 else None,
    }
    regions = json.load(open(os.path.join(CHAR, "regions.json"), encoding="utf-8"))
    for name, path in srcs.items():
        if not path or not os.path.exists(path):
            print("skip", name); continue
        im = Image.open(path).convert("RGB")
        a = np.array(im)
        a = clean_watermark(a)
        rgba = to_rgba(a)
        ann = analyze(rgba, name)
        out = Image.fromarray(rgba, "RGBA")
        # 缩放到原版画布：保持人物高度比例，脸对齐原版脸位
        scale = ORIG_H / out.size[1]
        out = out.resize((int(out.size[0]*scale), ORIG_H), Image.LANCZOS)
        canvas = Image.new("RGBA", (ORIG_W, ORIG_H), (0, 0, 0, 0))
        ox = (ORIG_W - out.size[0]) // 2
        canvas.paste(out, (ox, 0), out)
        canvas.save(os.path.join(CHAR, f"{name}.png"))
        # 标注换算到新版坐标
        def scv(v): return [round(v[0]*scale+ox), round(v[1]*scale)]
        fx, fy, fw, fh = ann["face"]
        regions[name] = {
            "alpha": True, "size": [ORIG_W, ORIG_H], "cut": [],
            "flower": scv(ann["flower"]) + [60],
            "chin": scv(ann["chin"]),
            "brooch": [scv(ann["chin"])[0], scv(ann["chin"])[1] + 170, 34],
            "face": [round(fx*scale+ox), round(fy*scale), round(fw*scale), round(fh*scale)],
            "figure": [6, 17, ORIG_W-9, ORIG_H-25],
            "crops": {"avatar": [round(fx*scale+ox)-60, max(0,round(fy*scale)-200), round(fw*scale)+120, round(fw*scale)+120],
                       "bust": [max(0,ox), 0, out.size[0], min(ORIG_H, round(out.size[1]*0.8))]},
            "notes": "Qwen version, AIGC three-ink silhouette (processed by tools/qwen_art.py).",
        }
        print("wrote", name, "face", regions[name]["face"], "chin", regions[name]["chin"])
    json.dump(regions, open(os.path.join(CHAR, "regions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("regions.json updated")

if __name__ == "__main__":
    main()
