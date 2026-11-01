# qwen_profile.py — turn the generated profile into a film asset.
# The generator baked its transparency checkerboard into pixels (two neutral greys), so: flood-fill the
# neutral-light background away from the border, quantise what is left to the film's three inks, then fit
# the figure into the same 1086x1448 canvas the other busts use.
import sys
from collections import deque
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else 'out/profile_gen/Flat_vector_cut_paper_illustra_2026-11-01T07-48-58.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/character/qwen_profile.png'
W_OUT, H_OUT = 1086, 1448
CREAM, MID, BLACK = (244, 224, 198), (71, 75, 111), (36, 26, 21)

im = Image.open(SRC).convert('RGB')
w, h = im.size
px = im.load()


def neutral_light(c):
    r, g, b = c
    return max(r, g, b) - min(r, g, b) <= 10 and min(r, g, b) >= 214


# background = neutral light pixels connected to the border
bg = bytearray(w * h)
q = deque()
for x in range(w):
    q.append((x, 0)); q.append((x, h - 1))
for y in range(h):
    q.append((0, y)); q.append((w - 1, y))
while q:
    x, y = q.popleft()
    if not (0 <= x < w and 0 <= y < h):
        continue
    i = y * w + x
    if bg[i] or not neutral_light(px[x, y]):
        continue
    bg[i] = 1
    q.append((x + 1, y)); q.append((x - 1, y)); q.append((x, y + 1)); q.append((x, y - 1))

# quantise: every non-background pixel to the nearest of the three inks
INK = [CREAM, MID, BLACK]


def nearest(c):
    best, bd = CREAM, 1e18
    for k in INK:
        d = (c[0] - k[0]) ** 2 + (c[1] - k[1]) ** 2 + (c[2] - k[2]) ** 2
        if d < bd:
            bd, best = d, k
    return best


out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
op = out.load()
minx, miny, maxx, maxy = w, h, 0, 0
for y in range(h):
    for x in range(w):
        i = y * w + x
        if bg[i]:
            continue
        op[x, y] = nearest(px[x, y]) + (255,)
        if x < minx: minx = x
        if x > maxx: maxx = x
        if y < miny: miny = y
        if y > maxy: maxy = y

crop = out.crop((minx, miny, maxx + 1, maxy + 1))
cw, ch = crop.size
print('figure bbox', (minx, miny, maxx, maxy), 'size', crop.size)

# fit by height into the standard canvas, centred
k = H_OUT / ch
nw, nh = max(1, round(cw * k)), H_OUT
if nw > W_OUT:                       # never wider than the canvas: fit by width instead
    k = W_OUT / cw
    nw, nh = W_OUT, max(1, round(ch * k))
crop = crop.resize((nw, nh), Image.LANCZOS)
canvas = Image.new('RGBA', (W_OUT, H_OUT), (0, 0, 0, 0))
canvas.paste(crop, ((W_OUT - nw) // 2, (H_OUT - nh) // 2), crop)
canvas.save(OUT)
print('wrote', OUT, canvas.size, 'figure', (nw, nh), 'at x', (W_OUT - nw) // 2)
