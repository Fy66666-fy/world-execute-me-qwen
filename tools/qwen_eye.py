# qwen_eye.py — the generated face close-up into the film's three inks, at the size the film registers.
# No cropping (the registration of the iris is measured on the full canvas): flood the neutral background
# away from the border, quantise the rest, resize to 1254x1254.
import sys
from collections import deque
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else 'out/profile_gen/Extreme_close_up_of_the_SAME_c_2026-11-01T09-11-06.png'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'assets/character/qwen_eye.png'
SIZE = 1254
CREAM, MID, BLACK = (244, 224, 198), (71, 75, 111), (36, 26, 21)

im = Image.open(SRC).convert('RGB')
w, h = im.size
px = im.load()


def neutral_light(c):
    r, g, b = c
    return max(r, g, b) - min(r, g, b) <= 9 and min(r, g, b) >= 232


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
for y in range(h):
    for x in range(w):
        if bg[y * w + x]:
            continue
        op[x, y] = nearest(px[x, y]) + (255,)

out = out.resize((SIZE, SIZE), Image.LANCZOS)
out.save(OUT)
print('wrote', OUT, out.size, 'background px removed:', sum(bg), '/', w * h)
