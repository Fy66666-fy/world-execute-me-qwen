# Bust v4: the user's final bust (dark grey-violet hair, blue-violet petal backdrop, Qwen mark +
# tassel ornament, white jacket). Pipeline:
#   1. backdrop removed: region-grow from the TOP / LEFT / RIGHT borders over the backdrop tones
#      (the petals are gradient violet; growth is local-continuity, it stops at the figure's outline;
#      the bottom border is excluded - the jacket reaches it and must not be eaten)
#   2. every figure pixel quantised to the nearest of the three seed inks the engine expects:
#      cream 244,224,198 (jacket, mark, tassel) / mid 91,92,128 (hair, the figure's own grey-violet,
#      classified through art.js INK_SEEDS.qwen_bust) / black 36,26,21 (face, trims, bow)
#   3. scaled to fit the standard 1128x1452 canvas (fit width, centred vertically)
# Usage: python qwen_bust2.py <src.png> [out.png]
import sys
from collections import deque
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\方圆\.workbuddy\clipboard-images\clipboard-2026-10-31T16-03-50-945Z-169458fb.png"
OUT = sys.argv[2] if len(sys.argv) > 2 else "assets/character/qwen_bust.png"
CW, CH = 1128, 1452                     # the standard bust canvas (matches the other arts' aspect use)
CREAM, MID, BLACK = (244, 224, 198), (71, 75, 111), (36, 26, 21)   # mid = the hair's own grey-violet-blue

im = Image.open(SRC).convert("RGB")
w0, h0 = im.size
im = im.resize((int(w0 * CH / h0 * 0) + w0, h0))            # placeholder (no upscale: source is big enough)
px = im.load()
w, h = im.size

def near(a, b, tol):
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol and abs(a[2] - b[2]) <= tol

# ---- 1. backdrop: grow from the top / left / right borders over the backdrop tones ----
seeds = []
for x in range(w):                        # top border: all backdrop
    seeds.append(px[x, 0])
for y in range(h // 2):                   # side borders above the jacket
    seeds.append(px[0, y]); seeds.append(px[w - 1, y])
# quantise the seeds coarsely so the flood has a compact palette (drop near-white: the jacket)
pal = set()
for c in seeds:
    if (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255 > 0.72:
        continue
    pal.add((c[0] // 20 * 10, c[1] // 20 * 10, c[2] // 20 * 10))
bg = bytearray(w * h)
q = deque()
for x in range(w):
    q.append((x, 0))
for y in range(h // 2):
    q.append((0, y)); q.append((w - 1, y))
while q:
    x, y = q.popleft()
    i = y * w + x
    if bg[i]:
        continue
    p = px[x, y]
    key = (p[0] // 20 * 10, p[1] // 20 * 10, p[2] // 20 * 10)
    hit = any(near(key, s, 26) for s in pal) or sum(p) < 150        # backdrop tones + the dark frame corners
    if not hit:
        continue
    bg[i] = 1
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        xx, yy = x + dx, y + dy
        if 0 <= xx < w and 0 <= yy < h and not bg[yy * w + xx]:
            q.append((xx, yy))

mask = bytearray(0 if bg[i] else 1 for i in range(w * h))

# repair: the backdrop field (91,92,128) is within the flood's tolerance of the hair's own tone
# (70,74,110), so the flood ate into the hair; re-add the hair tone inside the head area
for y in range(50, 430):
    for x in range(180, 560):
        i = y * w + x
        if not mask[i] and near(px[x, y], (70, 74, 110), 14):
            mask[i] = 1
# hole fill: any backdrop pocket fully enclosed by the figure is figure (the dark hair shadows, the
# gaps the repair re-opened); flood the complement from the borders, what it cannot reach is figure
outside = bytearray(w * h)
q = deque()
for x in range(w):
    q.append((x, 0)); q.append((x, h - 1))
for y in range(h):
    q.append((0, y)); q.append((w - 1, y))
while q:
    x, y = q.popleft()
    i = y * w + x
    if outside[i] or mask[i]:
        continue
    outside[i] = 1
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        xx, yy = x + dx, y + dy
        if 0 <= xx < w and 0 <= yy < h:
            j = yy * w + xx
            if not outside[j] and not mask[j]:
                q.append((xx, yy))
for i in range(w * h):
    if not mask[i] and not outside[i]:
        mask[i] = 1

for _ in range(2):                       # close pinholes
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
seen = bytearray(w * h)                  # drop islands under 60 px
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
        if len(comp) < 60:
            for i in comp:
                mask[i] = 0

# ---- 2. quantise to the nearest seed ink ----
inks = [CREAM, MID, BLACK]
out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
op = out.load()
for y in range(h):
    for x in range(w):
        i = y * w + x
        if not mask[i]:
            continue
        p = px[x, y]
        best, bd = 0, 1 << 30
        for k, c in enumerate(inks):
            d = (p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2
            if d < bd:
                bd, best = d, k
        op[x, y] = (*inks[best], 255)

# ---- 3. onto the standard canvas: fit width, centred vertically ----
sc = CW / w
nw, nh = CW, int(round(h * sc))
out = out.resize((nw, nh), Image.LANCZOS)
oy = (CH - nh) // 2
canvas = Image.new("RGBA", (CW, CH), (0, 0, 0, 0))
canvas.paste(out, (0, oy), out)
canvas.save(OUT)
print(f"wrote {OUT}  {CW}x{CH}  (figure {nw}x{nh}, offset y {oy}, mid ink {MID})")
