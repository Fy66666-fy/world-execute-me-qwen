# Converts the provided Qwen fan-figure image (blue-haired bust, dark circular backdrop) into the
# film's three-ink cut-paper format, and dresses her with the film's own ornament:
#   1. background removed (region-grow from the border; it stops at the figure)
#   2. quantised to the THREE SEED INKS the engine expects (cream 244,224,198 / orange-slot 220,114,63 /
#      black 36,26,21) - the file colour of the middle ink does not matter on screen (plates print in
#      palette roles), only that the classifier sorts it right: hair -> middle ink (printed indigo)
#   3. the whale ornament erased (its patch printed back as flat hair)
#   4. the TASSEL from cat_bust.png (the film's own folded streamers, black/cream) flood-extracted
#      from between the orange hair and hung under the mark
#   5. the official Qwen mark (out/qwen_mark.png, rendered from motif.js's verbatim paths) as the flower
# Usage: python qwen_bust.py <src.png> [out.png]
import sys
from collections import deque
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\方圆\.workbuddy\clipboard-images\clipboard-2026-10-31T12-38-48-651Z-482998e1.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/character/qwen_bust.png"
S = 4                                    # upscale factor: the source is small, the tracer wants pixels
CREAM, MID, BLACK = (244, 224, 198), (72, 82, 196), (36, 26, 21)   # mid ink = the project's figure blue-violet
WHALE = (440, 95, 740, 320)              # 4x coords: the whale ornament, erased back to flat hair
MARK = (512, 512, 0.46, 640, 196)        # out/qwen_mark.png: (file size, scale, centre x, centre y)
TASSEL = "assets/character/cat_bust.png"
T_SEED = (870, 392)                      # a point on the cat's black ribbon
T_BOX = (762, 296, 1022, 752)            # strictly below the flower, right of the hair
T_AT = (0.92, 640, 262)                  # (scale, centre x of the ribbon, top y) on the figure

im = Image.open(SRC).convert("RGB")
w, h = im.size
im = im.resize((w * S, h * S), Image.LANCZOS)
w, h = im.size
px = im.load()

# ---- 1. background: grow from every border pixel while the LOCAL step stays flat (stops at the figure) ----
bg = bytearray(w * h)
q = deque()
for x in range(w):
    q.append((x, 0)); q.append((x, h - 1))
for y in range(h):
    q.append((0, y)); q.append((w - 1, y))
def near(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol and abs(a[2] - b[2]) <= tol
while q:
    x, y = q.popleft()
    i = y * w + x
    if bg[i]:
        continue
    p = px[x, y]
    if near(p, (0, 0, 0), 8) or near(p, (24, 24, 40), 26) or near(p, (40, 48, 96), 30) or near(p, (16, 32, 48), 22) or near(p, (0, 32, 48), 22):
        bg[i] = 1
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            xx, yy = x + dx, y + dy
            if 0 <= xx < w and 0 <= yy < h and not bg[yy * w + xx]:
                q.append((xx, yy))

mask = bytearray(0 if bg[i] else 1 for i in range(w * h))
for _ in range(2):                       # close pinholes: a pixel hemmed in by figure becomes figure
    fix = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            i = y * w + x
            if not mask[i]:
                n = mask[i - 1] + mask[i + 1] + mask[i - w] + mask[i + w]
                if n >= 3:
                    fix.append(i)
    for i in fix:
        mask[i] = 1
seen = bytearray(w * h)                  # drop islands under 40 px (dust outside the figure)
for start in range(w * h):
    if mask[start] and not seen[start]:
        comp = [start]; seen[start] = 1; k = 0
        while k < len(comp):
            i = comp[k]; k += 1
            x, y = i % w, i // w
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                j = yy * w + xx
                if 0 <= xx < w and 0 <= yy < h and mask[j] and not seen[j]:
                    seen[j] = 1; comp.append(j)
        if len(comp) < 40:
            for i in comp:
                mask[i] = 0

# ---- 2. quantise ----
ink = bytearray(w * h)                   # 0 = none, 1 = cream, 2 = mid, 3 = black
for y in range(h):
    for x in range(w):
        i = y * w + x
        if not mask[i]:
            continue
        r, g, b = px[x, y]
        mx, mn = max(r, g, b), min(r, g, b)
        lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
        sat = (mx - mn) / mx if mx else 0
        ink[i] = 3 if lum < 0.30 else 1 if (sat < 0.28 and lum >= 0.62) else 2

# ---- 3. the whale: its patch becomes hair again, out to the head's own silhouette ----
# The hair edge as it would run without the whale (4x coords), traced from the source and rounded out:
CUT = [(640, 100), (700, 160), (750, 230), (780, 300), (795, 360), (788, 420), (768, 472)]
def edge_x(y):
    for (x0, y0), (x1, y1) in zip(CUT, CUT[1:]):
        if y0 <= y <= y1:
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    return None
# repair: the background flood leaked into the hair's own dark shadow behind the whale (the two tones
# are near-identical); re-add the shadow tone there, it is real hair
for y in range(240, 660):
    for x in range(470, 710):
        i = y * w + x
        if not mask[i] and near(px[x, y], (0, 32, 32), 15):
            mask[i] = 1; ink[i] = 3
for y in range(100, 472):
    ex = edge_x(y)
    for x in range(540, 920):
        i = y * w + x
        if x > ex:
            mask[i] = 0; ink[i] = 0              # the whale over the backdrop: gone
        elif mask[i]:
            ink[i] = 2                           # the whale over the hair: flat hair

# ---- 3b. the stray strands: the reconstructed side was smooth, so mirror the head's own left-edge
# spikes over it (add-only: real strands from this very figure, never over the ornament or shadows)
for y in range(130, 500):
    for x in range(60, 390):
        i = y * w + x
        if not mask[i] or ink[i] == 0:
            continue
        mx = 900 - x
        if not (510 <= mx < w):
            continue
        j = y * w + mx
        if ink[j] == 0 or ink[j] == 2:
            mask[j] = 1
            ink[j] = ink[i]

# ---- 4. the cat's tassel, hung under the mark ----
cat = Image.open(TASSEL).convert("RGB")
cp = cat.load()
cw, ch = cat.size
seed = T_SEED
tmask = {}
q = deque([seed])
while q:
    x, y = q.popleft()
    if (x, y) in tmask or not (T_BOX[0] <= x < T_BOX[2] and T_BOX[1] <= y < T_BOX[3]):
        continue
    p = cp[x, y]
    if not (near(p, CREAM, 34) or near(p, BLACK, 34)):
        continue
    tmask[(x, y)] = CREAM if near(p, CREAM, 34) else BLACK
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        q.append((x + dx, y + dy))
xs = [p[0] for p in tmask]; ys = [p[1] for p in tmask]
bx0, bx1, by0, by1 = min(xs), max(xs), min(ys), max(ys)
print(f"tassel extracted: {len(tmask)} px, bbox {bx0}..{bx1} x {by0}..{by1}")
sc, tcx, tty = T_AT
for (x, y), c in tmask.items():
    nx = int(tcx + (x - (bx0 + bx1) / 2) * sc)
    ny = int(tty + (y - by0) * sc)
    if 0 <= nx < w and 0 <= ny < h:
        ink[ny * w + nx] = 1 if c == CREAM else 3
        mask[ny * w + nx] = 1

# ---- 5. the mark as the flower ----
mark = Image.open("out/qwen_mark.png").convert("RGBA")
mw, mh = mark.size
mp = mark.load()
ms = MARK[2]
dw, dh = int(mw * ms), int(mh * ms)
for y in range(dh):
    for x in range(dw):
        a = mp[int(x / ms), int(y / ms)][3]
        if a > 120:
            nx, ny = MARK[3] - dw // 2 + x, MARK[4] - dh // 2 + y
            if 0 <= nx < w and 0 <= ny < h:
                i = ny * w + nx
                ink[i] = 1
                mask[i] = 1

# ---- paint and save ----
out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
op = out.load()
COL = {1: CREAM, 2: MID, 3: BLACK}
for i, k in enumerate(ink):
    if k:
        x, y = i % w, i // w
        op[x, y] = (*COL[k], 255)
out.save(OUT)
print(f"wrote {OUT}  {w}x{h}")
