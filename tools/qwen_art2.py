# Qwen 版素材处理 v2：裁胸像 → 清右下角水印 → 三色量化+透明底 → 缩放到 1086x1448 → 检测标注。
# 用法: python tools/qwen_art2.py <src.png> <name> <crop_y1> [crop_x0 crop_x1]
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")
INKS = np.array([[244, 224, 198], [72, 82, 196], [36, 26, 21]], dtype=np.float64)
ORIG_W, ORIG_H = 1086, 1448

def process(src, name, crop_y1, crop_x0=0, crop_x1=None):
    im = Image.open(src).convert("RGB")
    W0, H0 = im.size
    a = np.array(im)[0:crop_y1, crop_x0:(crop_x1 or W0), :]
    H, W = a.shape[:2]
    lum = a.mean(2)
    # 1) 水印清理：右下角区域内，亮像素且其 9px 邻域存在蓝/暗像素 → 填蓝
    y0, x0 = int(H * 0.88), int(W * 0.55)
    reg = a[y0:, x0:].copy(); rl = lum[y0:, x0:]
    near_dark = ndimage.maximum_filter(((rl < 160)).astype(np.uint8), size=13) > 0
    hit = (rl > 175) & near_dark
    lab, n = ndimage.label(hit)
    for i in range(1, n + 1):
        m = lab == i
        if m.sum() < 6000: reg[m] = [72, 82, 196]
    a[y0:, x0:] = reg
    # 2) 量化三色 + 白底转透明
    lum = a.mean(2)
    alpha = np.where(lum > 235, 0, 255).astype(np.uint8)
    d = ((a[..., None, :] - INKS[None, None, :, :]) ** 2).sum(-1)
    q = d.argmin(-1)
    rgb = INKS[q].astype(np.uint8)
    rgba = np.dstack([rgb, alpha])
    # 3) 缩放到画布（人物高度=画布高，宽按比例，居中）
    scale = ORIG_H / H
    nw = int(round(W * scale))
    img = Image.fromarray(rgba, "RGBA").resize((nw, ORIG_H), Image.LANCZOS)
    canvas = Image.new("RGBA", (ORIG_W, ORIG_H), (0, 0, 0, 0))
    ox = (ORIG_W - nw) // 2
    canvas.paste(img, (ox, 0), img)
    canvas.save(os.path.join(CHAR, f"{name}.png"))
    # 4) 检测标注（在新画布坐标）
    A = np.array(canvas)
    al = A[:, :, 3] > 128
    L = A[:, :, :3].mean(2)
    dark = al & (L < 70)
    # 眼睛候选：y ∈ [0.10H,0.38H] 的暗块，面积 30~3000
    zone = np.zeros_like(dark); zone[int(ORIG_H*0.10):int(ORIG_H*0.38), :] = True
    ev = dark & zone
    lab, n = ndimage.label(ev)
    eyes = []
    for i in range(1, n + 1):
        m = lab == i
        if 30 <= m.sum() <= 3000:
            ys, xs = np.where(m)
            eyes.append((xs.mean(), ys.mean(), m.sum()))
    eyes.sort(key=lambda e: -e[2])
    eyes = eyes[:4]
    print(name, "eye candidates:", [(round(x), round(y), int(s)) for x, y, s in eyes])
    ys, xs = np.where(al)
    print(name, "figure bbox:", int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()), "scale", round(scale, 3), "ox", ox)

if __name__ == "__main__":
    src, name = sys.argv[1], sys.argv[2]
    crop_y1 = int(sys.argv[3])
    cx0 = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    cx1 = int(sys.argv[5]) if len(sys.argv) > 5 else None
    process(src, name, crop_y1, cx0, cx1)
