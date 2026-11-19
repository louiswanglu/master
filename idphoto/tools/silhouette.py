#!/usr/bin/env python3
"""Recover the bust silhouette (alpha) for the ID photo.

Why plain segmentation fails
----------------------------
The selfie was taken in an office chair in front of a bookshelf.  Vision's
person- and foreground-instance masks both keep the dark chair backrest, so a
naive cutout leaves grey wedges on the white ID background beside the shoulders
and a dark block next to the neck.

What works instead
------------------
1. Shoulder line.  The knit sweater is the only blue-dominant material in frame
   (B-R up to +60, versus 0..10 on the neutral grey chair), so the topmost
   *sustained* row of blue knit per column is the true shoulder edge.  A rolling
   maximum removes the neckline dip and double smoothing gives one clean curve;
   everything below it is torso.  The chair backrest lies above the curve and is
   therefore excluded by construction.
2. Head, hair and ears.  The Vision instance mask is excellent there; it is only
   restricted by a soft face-centred ellipse, and from the jaw down by the
   measured skin width, so nothing dark can ride along beside the neck.
3. Neck.  Below the jaw the mask is not used at all: the neck silhouette is
   interpolated from the skin-width at the jaw to the torso width at the collar.
   That is always a clean tapering shape and includes the shadow under the chin.

The union is reduced to the component containing the face, holes are filled so
the bust is one solid shape, and the edge is softened by 0.9 px.

Writes build/alpha.png + previews.
"""
import json
import os
from collections import deque

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD = os.path.join(ROOT, "build")


# ----------------------------------------------------------------- helpers
def fill_holes(binary):
    h, w = binary.shape
    free = ~binary
    seen = np.zeros((h, w), bool)
    q = deque()
    for x in range(w):
        for y in (0, h - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if free[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((y, x))
    while q:
        y, x = q.popleft()
        for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((ny, nx))
    return binary | (free & ~seen)


def largest_bridged(binary, r=18):
    """Largest connected component after dilating by r px, eroded back."""
    d = np.asarray(Image.fromarray((binary * 255).astype(np.uint8))
                   .filter(ImageFilter.MaxFilter(2 * r + 1))) > 127
    h, w = d.shape
    seen = np.zeros((h, w), bool)
    ys, xs = np.nonzero(d)
    best, best_n = None, 0
    step = max(1, len(ys) // 800)
    for i in range(0, len(ys), step):
        sy, sx = int(ys[i]), int(xs[i])
        if seen[sy, sx]:
            continue
        q = deque([(sy, sx)])
        seen[sy, sx] = True
        comp = []
        while q:
            y, x = q.popleft()
            comp.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and d[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if len(comp) > best_n:
            best, best_n = comp, len(comp)
    out = np.zeros((h, w), bool)
    yy, xx = zip(*best)
    out[list(yy), list(xx)] = True
    return np.asarray(Image.fromarray((out * 255).astype(np.uint8))
                      .filter(ImageFilter.MinFilter(2 * r + 1))) > 127


def smoothstep(x, e0, e1):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------- inputs
src = np.asarray(Image.open(os.path.join(ROOT, "source.png")).convert("RGB"),
                 dtype=np.float32) / 255.0
inst = np.asarray(Image.open(os.path.join(BUILD, "fgmask.png")).convert("L"),
                  dtype=np.float32) / 255.0
face = json.load(open(os.path.join(BUILD, "face.json")))["faces"][0]
H, W = inst.shape

R, G, B = src[..., 0], src[..., 1], src[..., 2]
L = 0.2126 * R + 0.7152 * G + 0.0722 * B
blue = (B - R) * 255.0
warm = (R - B) * 255.0

chin_y = float(max(face["faceContour"], key=lambda p: p["y"])["y"])
eyes = face["leftEye"] + face["rightEye"]
ex = float(np.mean([p["x"] for p in eyes]))
ey = float(np.mean([p["y"] for p in eyes]))
print(f"eye ({ex:.1f},{ey:.1f})  chin y {chin_y:.1f}")

yy, xx = np.mgrid[0:H, 0:W]

# ------------------------------------------------------- 1. shoulder curve
knit = (blue > 12) & (L < 0.72)
top = np.full(W, np.nan)
for x in range(W):
    hits = np.nonzero(knit[520:, x])[0] + 520
    for y0 in hits:
        if knit[y0:y0 + 70, x].mean() > 0.6:       # sustained knit, not a stray
            top[x] = float(y0)
            break

xs = np.arange(W)
ok = ~np.isnan(top)
top = np.interp(xs, xs[ok], top[ok])
win = 110                                          # rolling max kills the neckline dip
env = np.array([top[max(0, i - win):i + win + 1].max() for i in range(W)])
k = 25
curve = np.convolve(np.pad(env, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
curve = np.convolve(np.pad(curve, (k, k), mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), "valid")
print("shoulder curve @ x=88,256,512,716,900: "
      + ", ".join(f"{curve[x]:.0f}" for x in (88, 256, 512, 716, 900)))

torso = np.clip(yy - curve[None, :] + 0.5, 0.0, 1.0).astype(np.float32)

torso = np.clip(yy - curve[None, :] + 0.5, 0.0, 1.0).astype(np.float32)

# -------------------------------------------------- 2. skin width per row
skin = (warm > 6) & (L > 0.14) & (L < 0.88)
skin = np.asarray(Image.fromarray((skin * 255).astype(np.uint8))
                  .filter(ImageFilter.MedianFilter(7))) > 127
skin_lo = np.full(H, np.nan)
skin_hi = np.full(H, np.nan)
for y in range(int(ey), H):
    row = skin[y]
    if not row[int(ex)]:
        continue
    lo = int(ex)
    while lo > 0 and row[lo - 1]:
        lo -= 1
    hi = int(ex)
    while hi < W - 1 and row[hi + 1]:
        hi += 1
    skin_lo[y], skin_hi[y] = lo, hi


def smooth_curve(v, win=9, passes=4):
    v = v.copy()
    for _ in range(passes):
        out = v.copy()
        for i in range(len(v)):
            seg = v[max(0, i - win):i + win + 1]
            seg = seg[~np.isnan(seg)]
            if len(seg):
                out[i] = np.median(seg)
        v = out
    return v


skin_lo = smooth_curve(skin_lo)
skin_hi = smooth_curve(skin_hi)
known = np.nonzero(~np.isnan(skin_lo))[0]
face_lo = np.interp(np.arange(H), known, skin_lo[known])
face_hi = np.interp(np.arange(H), known, skin_hi[known])
# The warm-skin run survives into the deep shadow on the right side of the neck,
# and cutting there leaves a dark line on the white background.  Trim to the last
# reasonably lit pixel of each row so the silhouette edge sits on lit skin.
lit = L > 0.30
for y in range(int(ey), H):
    lo, hi = int(face_lo[y]), int(face_hi[y])
    if hi - lo < 30:
        continue
    xr = hi
    while xr > lo and not lit[y, xr]:
        xr -= 1
    if hi - xr <= 14 and xr > lo:
        face_hi[y] = xr + 1
    xl = lo
    while xl < hi and not lit[y, xl]:
        xl += 1
    if xl - lo <= 14 and xl < hi:
        face_lo[y] = xl - 1
# A second, wider smoothing pass on the neck band only: the raw skin run is noisy
# where the shadow under the jaw fades, which would read as a jagged edge at
# print size.  Rows outside the band are left untouched.
band0, band1 = int(chin_y) - 90, int(min(curve[int(ex)], H - 1))
for arr in (face_lo, face_hi):
    seg = arr[band0:band1].copy()
    for _ in range(6):
        sm = seg.copy()
        for i in range(len(seg)):
            sm[i] = seg[max(0, i - 16):i + 17].mean()
        seg = sm
    arr[band0:band1] = seg
y_collar = band1 - 8

# ------------------------------------------------------------ 3. head
ellipse = ((xx - ex) / 214.0) ** 2 + ((yy - (ey + 22)) / 297.0) ** 2
head = inst * np.clip(1 - smoothstep(ellipse, 0.80, 1.10), 0, 1)
# From the jaw down, clamp to the measured skin width; below that the analytic
# neck takes over entirely so no dark chair pixel can survive next to the neck.
jaw = chin_y - 35
clamp = smoothstep(yy, jaw - 60, jaw)
width_ok = np.clip(np.minimum(xx - (face_lo[:, None] - 3), (face_hi[:, None] + 3) - xx), 0, 1)
head *= (1 - clamp) + clamp * width_ok
head *= 1 - smoothstep(yy, chin_y + 8, chin_y + 48)

# ------------------------------------------------------------ 4. neck
# The neck silhouette follows the measured skin width row by row, so the edge
# sits exactly on the real jaw/neck boundary (including the shadow under the
# chin) and never on the chair behind it.
lo_ext = face_lo + 1.0
hi_ext = face_hi - 1.0
neck = np.clip(np.minimum(xx - lo_ext[:, None] + 0.5, hi_ext[:, None] - xx + 0.5), 0, 1)
neck = neck.astype(np.float32)
neck *= np.clip(smoothstep(yy, jaw - 40, jaw + 5), 0, 1)         # fade in under the jaw
neck *= np.clip((curve[None, :] - yy) / 4.0 + 0.6, 0, 1)        # stop at the collar
neck = np.asarray(Image.fromarray((neck * 255).astype(np.uint8))
                  .filter(ImageFilter.GaussianBlur(2)), dtype=np.float32) / 255.0
print(f"neck y {int(jaw)}..{int(y_collar)}: "
      f"x[{lo_ext[int(chin_y)]:.0f},{hi_ext[int(chin_y)]:.0f}] at the chin")

# ------------------------------------------------------------ 5. combine
person = np.clip(np.maximum.reduce([torso, head, neck]), 0, 1)
person = np.clip((person - 0.08) / 0.88, 0, 1)

main = fill_holes(largest_bridged(person > 0.45))
person = np.maximum(person * main, main.astype(np.float32))

alpha = np.asarray(Image.fromarray((person * 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.9)), dtype=np.float32) / 255.0

# ------------------------------------------- 6. drop deep-shadow slivers
# Where the silhouette would end inside a shadowed crease (the shaded side of the
# neck, under the jaw), the cut lands on near-black pixels and leaves a dark line
# on the white background.  Compare each pixel with the local brightness of the
# solid body around it and pull the matte back off anything much darker.
def box_mean(img, r):
    k = 2 * r + 1
    pad = np.pad(img, r, mode="reflect")
    s = pad.cumsum(0).cumsum(1)
    s = np.pad(s, ((1, 0), (1, 0)), mode="constant")
    return (s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]) / (k * k)


solid = (alpha > 0.6).astype(np.float32)
weight = box_mean(solid, 9)
local = box_mean(L * solid, 9) / np.maximum(weight, 1e-3)
local_safe = np.where(weight > 0.25, local, np.nanmean(local[weight > 0.25]))
ratio = L / np.maximum(local_safe, 0.05)
shadow = np.clip((0.55 - ratio) / 0.25, 0, 1)          # 1 when far darker than local
shadow = np.asarray(Image.fromarray((shadow * 255).astype(np.uint8))
                    .filter(ImageFilter.GaussianBlur(2)), dtype=np.float32) / 255.0
# Only the silhouette rim is of interest: interior dark detail (pupils, brows,
# nostrils) is legitimate and must not be touched.
eroded = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8))
                    .filter(ImageFilter.MinFilter(25)), dtype=np.float32) / 255.0
rim = np.clip(alpha - eroded, 0, 1)
alpha = np.clip(alpha - 1.15 * shadow * rim * alpha, 0, 1)
print(f"shadow slivers suppressed at {int((shadow * rim > 0.5).sum())} px")
print(f"alpha coverage {(alpha > 0.5).mean():.4f}  "
      f"rows {np.nonzero(alpha.any(1))[0].min()}..{np.nonzero(alpha.any(1))[0].max()}")

Image.fromarray((alpha * 255).astype(np.uint8)).save(os.path.join(BUILD, "alpha.png"))

over = (src * 255).astype(np.uint8)
over[(alpha > 0.30) & (alpha < 0.80)] = [255, 40, 40]
Image.fromarray(over).resize((760, 760), Image.LANCZOS).save(os.path.join(BUILD, "mask_overlay_small.png"))

cut = (src * 255 * alpha[..., None] + 255 * (1 - alpha[..., None])).astype(np.uint8)
Image.fromarray(cut).save(os.path.join(BUILD, "mask_cutout.png"))
Image.fromarray(cut).resize((760, 760), Image.LANCZOS).save(os.path.join(BUILD, "mask_cutout_small.png"))
print("wrote alpha.png + previews")
