#!/usr/bin/env python3
"""Build a clean ID-style portrait from the supplied selfie.

Pipeline
--------
1. tools/silhouette.py  -> clean bust alpha (see that file for why plain
   segmentation cannot work on this photo)
2. guided-filter matte refinement around the existing alpha edge
3. rim colour decontamination against the bright room backdrop
4. restrained studio grade (no filter look, natural skin)
5. 2.5x Lanczos upsample, pure-white composite
6. ID crop: head 2/3 of frame, 5:7 aspect, eyes on the upper third
7. unsharp mask, JPEG under 1 MB at 300 dpi

Usage:  python3 tools/build.py
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")


# --------------------------------------------------------------------- utils
def box_blur(img, r):
    """Mean filter, (2r+1)^2 window, via summed-area table."""
    squeeze = img.ndim == 2
    if squeeze:
        img = img[:, :, None]
    h, w, c = img.shape
    pad = np.pad(img, ((r + 1, r), (r + 1, r), (0, 0)), mode="reflect")
    s = pad.cumsum(0).cumsum(1)
    s = np.pad(s, ((1, 0), (1, 0), (0, 0)), mode="constant")
    k = 2 * r + 1
    out = (s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]) / (k * k)
    out = out[:h, :w]
    return out[:, :, 0] if squeeze else out


def guided_filter(guide, src, r, eps):
    mI, mP = box_blur(guide, r), box_blur(src, r)
    varI = box_blur(guide * guide, r) - mI ** 2
    covIP = box_blur(guide * src, r) - mI * mP
    a = covIP / (varI + eps)
    b = mP - a * mI
    return box_blur(a, r) * guide + box_blur(b, r)


def smoothstep(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def luminance(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def unsharp(rgb, radius, amount, threshold=0.0):
    pil = Image.fromarray(np.clip(rgb * 255, 0, 255).astype(np.uint8))
    b = np.asarray(pil.filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0
    diff = rgb - b
    if threshold > 0:
        diff = np.where(np.abs(diff) < threshold, 0.0, diff)
    return np.clip(rgb + amount * diff, 0, 1)


# --------------------------------------------------------------------- load
src = np.asarray(Image.open(os.path.join(ROOT, "source.png")).convert("RGB"),
                 dtype=np.float32) / 255.0
alpha = np.asarray(Image.open(os.path.join(BUILD, "alpha.png")).convert("L"),
                   dtype=np.float32) / 255.0
face = json.load(open(os.path.join(BUILD, "face.json")))["faces"][0]
H, W = alpha.shape
print(f"source {W}x{H}")

# ------------------------------------------------- 1. matte edge refinement
# The silhouette comes from colour geometry; nudge the last few pixels onto the
# real hair/cloth edge with a luminance-guided filter, then keep the crisp core.
lum = luminance(src)
guided = guided_filter(lum, alpha, r=3, eps=0.0018)
edge_band = smoothstep(alpha, 0.02, 0.10) * (1 - smoothstep(alpha, 0.90, 0.98))
alpha = np.clip(alpha * (1 - edge_band) + guided * edge_band, 0, 1)

# ------------------------------------------------ 2. rim decontamination
# The room behind him is bright, so hair and cloth rims are pulled toward white.
# Un-mix against a bright neutral backdrop to recover the true colour.
BACKDROP = 0.94
a = np.clip(alpha, 1e-3, 1.0)[..., None]
recovered = src - (1 - a) * BACKDROP
recovered = np.clip(recovered / np.maximum(a, 0.30), 0, 1.25)
blend = smoothstep(alpha, 0.03, 0.80)[..., None]
person = np.clip(src * (1 - blend) + recovered * blend, 0, 1)

# The silhouette edge sometimes lands on a shadowed fold (neck, collar, hairline),
# which reads as a hard dark line once it sits on white.  Pull the outermost few
# pixels of solid coverage toward the colour just inside, with a smooth ramp.
inner = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                   .filter(ImageFilter.MinFilter(21)), dtype=np.float32) / 255.0
rim = np.clip(alpha - inner, 0, 1)
rim = smoothstep(rim, 0.0, 1.0)[..., None]
interior = np.asarray(
    Image.fromarray((person * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5)),
    dtype=np.float32) / 255.0
person = np.clip(person * (1 - 0.55 * rim) + interior * (0.55 * rim), 0, 1)

# ------------------------------------------------------- 3. studio grade
Y = np.clip(luminance(person), 0, 1)
gained = np.clip(Y + 0.12 * (Y - 0.5) * (1 - np.abs(Y - 0.5) * 1.5), 0, 1)
person = np.clip(person * (gained / np.maximum(Y, 1e-4))[..., None], 0, 1)
person = np.where(person > 0.92, 0.92 + (person - 0.92) * 0.55, person)  # keep highlights
Y2 = luminance(person)[..., None]
person = np.clip(Y2 + (person - Y2) * 1.05, 0, 1)                        # gentle saturation

# ------------------------------------------------------------ 4. upsample
# Upsample premultiplied colour, otherwise Lanczos ringing near the dark hair
# mixes with white and leaves a light halo along the silhouette.
SCALE = 2.5
up_w, up_h = int(W * SCALE), int(H * SCALE)
premult = person * alpha[..., None]
premult_up = np.asarray(
    Image.fromarray(np.clip(premult * 255, 0, 255).astype(np.uint8))
    .resize((up_w, up_h), Image.LANCZOS), dtype=np.float32) / 255.0
alpha_up = np.asarray(
    Image.fromarray((alpha * 255).astype(np.uint8)).resize((up_w, up_h), Image.LANCZOS),
    dtype=np.float32) / 255.0
alpha_up = np.clip(alpha_up, 0, 1)
person_up = np.clip(premult_up / np.maximum(alpha_up[..., None], 1e-3), 0, 1)
print(f"working canvas {up_w}x{up_h}")

# ------------------------------------------------------------- 5. geometry
chin = max(face["faceContour"], key=lambda p: p["y"])
eyes = face["leftEye"] + face["rightEye"]
eye_y = float(np.mean([p["y"] for p in eyes]))
eye_x = float(np.mean([p["x"] for p in eyes]))
ys, xs = np.nonzero(alpha > 0.5)
hair_top = float(ys.min())
head_h = float(chin["y"]) - hair_top
print(f"hair_top={hair_top:.0f} chin={chin['y']:.0f} head_h={head_h:.0f} "
      f"eye=({eye_x:.0f},{eye_y:.0f})")

HEAD_FRAC = 0.60         # head height / frame height (ID photo convention)
TOP_MARGIN = 0.075       # gap above the hair, as a fraction of frame height
ASPECT = 5 / 7           # 25 mm x 35 mm
crop_h = head_h / HEAD_FRAC
crop_w = crop_h * ASPECT
# the body is wider than the frame at the shoulders, so bias the crop between the
# face axis and the shoulder centre to keep the cut symmetrical
ys_body, xs_body = np.nonzero(alpha[int(chin["y"]):, :] > 0.5)
shoulder_cx = float(xs_body.mean())
cx_center = 0.62 * eye_x + 0.38 * shoulder_cx
crop_x0 = cx_center - crop_w / 2
crop_y0 = hair_top - TOP_MARGIN * crop_h
print(f"shoulder cx={shoulder_cx:.0f} crop centre x={cx_center:.0f}")
print(f"crop x[{crop_x0:.0f},{crop_x0 + crop_w:.0f}] "
      f"y[{crop_y0:.0f},{crop_y0 + crop_h:.0f}]")

cx0, cy0 = int(round(crop_x0 * SCALE)), int(round(crop_y0 * SCALE))
cw, ch = int(round(crop_w * SCALE)), int(round(crop_h * SCALE))

canvas_rgb = np.ones((ch, cw, 3), dtype=np.float32)
canvas_a = np.zeros((ch, cw), dtype=np.float32)
sx0, sy0 = max(0, cx0), max(0, cy0)
sx1, sy1 = min(up_w, cx0 + cw), min(up_h, cy0 + ch)
dx0, dy0 = sx0 - cx0, sy0 - cy0
dw, dh = sx1 - sx0, sy1 - sy0
canvas_rgb[dy0:dy0 + dh, dx0:dx0 + dw] = person_up[sy0:sy1, sx0:sx1]
canvas_a[dy0:dy0 + dh, dx0:dx0 + dw] = alpha_up[sy0:sy1, sx0:sx1]

crop = canvas_rgb * canvas_a[..., None] + (1.0 - canvas_a[..., None])
Image.fromarray((crop * 255).astype(np.uint8)).save(os.path.join(BUILD, "crop_work.png"))

if "--stage" in sys.argv:
    sys.exit(0)

# ---------------------------------------------------------------- 6. export
FINALS = [
    ("idphoto_2inch_1200x1680.jpg", 1200, 1680),
    ("idphoto_1inch_413x579.jpg", 413, 579),
]
for name, tw, th in FINALS:
    img = Image.fromarray((crop * 255).astype(np.uint8)).resize((tw, th), Image.LANCZOS)
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = unsharp(arr, radius=1.0, amount=0.5, threshold=0.005)
    img = Image.fromarray(np.clip(arr * 255, 0, 255).astype(np.uint8))
    path = os.path.join(ROOT, name)
    for q in (95, 93, 91, 89, 87, 85):
        img.save(path, "JPEG", quality=q, subsampling=0, dpi=(300, 300), optimize=True)
        size = os.path.getsize(path)
        if size <= 1_000_000:
            break
    print(f"{name}: {img.size} {size / 1024:.0f} KB q={q}")
