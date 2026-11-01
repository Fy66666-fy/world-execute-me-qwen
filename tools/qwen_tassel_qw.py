# f_bust / f_reach：抹掉帽下条纹缎带（cream+black → 蓝发），在帽徽下重画与六张 Claude 图同款的流苏。
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from qwen_ornament import CREAM, BLUE, BLACK, SS, tassel

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAR = os.path.join(ROOT, "assets", "character")

def ribbon_to_tassel(name, zone, anchor, R):
    p = os.path.join(CHAR, f"{name}.png")
    im = Image.open(p).convert("RGBA")
    a = np.array(im)
    x0, y0, x1, y1 = zone
    lum = a[:, :, :3].mean(2)
    al = a[:, :, 3] > 128
    cream = al & (lum > 150)
    dark = al & (lum < 90)
    zb = np.zeros(a.shape[:2], bool); zb[y0:y1, x0:x1] = True
    wipe = (cream | dark) & zb
    a[wipe, 0], a[wipe, 1], a[wipe, 2] = BLUE
    big = Image.fromarray(a, "RGBA").resize((im.width * SS, im.height * SS), Image.NEAREST)
    dr = ImageDraw.Draw(big)
    ax, ay = anchor
    tassel(dr, ax * SS, ay * SS, R * SS)
    big.resize(im.size, Image.LANCZOS).save(p)
    print(name, "wiped", int(wipe.sum()), "px, tassel at", anchor)

if __name__ == "__main__":
    # f_bust：缎带区在帽徽(330,300)正下方偏左；流苏从徽下出发
    ribbon_to_tassel("f_bust", (255, 348, 425, 705), (348, 342), 78)
    # f_reach：缎带区在帽徽(280,132)下方
    ribbon_to_tassel("f_reach", (245, 178, 362, 462), (296, 170), 62)
