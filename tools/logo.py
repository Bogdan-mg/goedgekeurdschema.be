"""Maakt logo-varianten en icoontjes uit img/logo-origineel.jpg (python3 tools/logo.py)."""
from PIL import Image, ImageDraw
import numpy as np

src = np.asarray(Image.open('img/logo-origineel.jpg').convert('RGB')).astype(float)
a = (255 - src).max(axis=2) / 255.0
a = np.clip((a - 0.03) / 0.97, 0, 1)          # jpeg-ruis op de witte achtergrond wegfilteren
safe = np.where(a > 0, a, 1)[..., None]
rgb = np.clip(255 - (255 - src) / safe, 0, 255)
rgba = np.dstack([rgb, a * 255]).astype(np.uint8)
ys, xs = np.where(a > 0.05)
full = rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1].copy()


def donker(arr):
    """Navy en grijs worden licht, groen blijft groen (voor donkere achtergronden)."""
    out = arr.copy().astype(float)
    r, g, b = out[..., 0], out[..., 1], out[..., 2]
    t = np.clip((g - b) / 50.0, 0, 1)[..., None]
    L = 0.299 * r + 0.587 * g + 0.114 * b
    n = np.clip(255 - L * 0.62, 0, 255)
    out[..., :3] = t * out[..., :3] + (1 - t) * np.clip(np.dstack([n, n + 2, n + 6]), 0, 255)
    return out.astype(np.uint8)


def save(arr, name, h):
    im = Image.fromarray(arr, 'RGBA')
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    im.save(name, 'WEBP', lossless=True, method=6)
    return im.size


print('logo', save(full, 'img/logo.webp', 132))
print('logo-donker', save(donker(full), 'img/logo-donker.webp', 132))

# Beeldmerk (de V) apart, zonder de "g" van de woordmerk
mark = rgba.copy()
mark[:, 600:] = 0
mark[350:, 540:] = 0
ys, xs = np.where(mark[..., 3] > 12)
mi = Image.fromarray(mark[ys.min():ys.max() + 1, xs.min():xs.max() + 1], 'RGBA')


def icoon(size, pad, bg):
    c = Image.new('RGBA', (size, size), bg)
    s = size * (1 - 2 * pad)
    k = min(s / mi.width, s / mi.height)
    mm = mi.resize((round(mi.width * k), round(mi.height * k)), Image.LANCZOS)
    c.alpha_composite(mm, ((size - mm.width) // 2, (size - mm.height) // 2))
    return c


wit = (255, 255, 255, 255)
icoon(512, .14, wit).save('img/icon-512.png')
icoon(192, .14, wit).save('img/icon-192.png')
icoon(180, .14, wit).convert('RGB').save('img/apple-touch-icon.png')
icoon(96, .04, (0, 0, 0, 0)).save('img/favicon.png')
icoon(48, .04, (0, 0, 0, 0)).save('favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])

# Deelbeeld (WhatsApp, Facebook, ...) 1200x630
og = Image.new('RGBA', (1200, 630), wit)
fi = Image.fromarray(full, 'RGBA')
fi = fi.resize((940, round(fi.height * 940 / fi.width)), Image.LANCZOS)
og.alpha_composite(fi, ((1200 - fi.width) // 2, (630 - fi.height) // 2 - 10))
ImageDraw.Draw(og).rectangle([0, 612, 1200, 630], fill=(20, 175, 117, 255))
og.convert('RGB').save('img/og.png', optimize=True)
