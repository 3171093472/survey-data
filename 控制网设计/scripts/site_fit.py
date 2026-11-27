# -*- coding: utf-8 -*-
"""在影像上识别湘江水面, 选定走线, 计算桥位与控制点影像坐标"""
import math
import os
import sys

from PIL import Image
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\imagery"
IMG = os.path.join(OUT, "siteA_z16.jpg")
MPP = 2.112          # 米/像素 (z=16, lat 27.91)
LON0, LON1 = 112.944946, 112.977905
LAT0, LAT1 = 27.897349, 27.926474     # 经度从左到右, 纬度从下到上
W = H = 1536

im = Image.open(IMG).convert("RGB")
a = np.asarray(im).astype(int)
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
water = (R < 85) & (G < 115) & (B < 100) & (G >= R)


def spans(row):
    m = water[row]
    out, start = [], None
    for x in range(W):
        if m[x] and start is None:
            start = x
        elif not m[x] and start is not None:
            if x - start > 40:
                out.append((start, x - 1))
            start = None
    if start is not None and W - start > 40:
        out.append((start, W - 1))
    return out


print("行号  水面区间(像素)  宽度(m)")
best = []
for y in range(500, 1300, 25):
    sp = spans(y)
    if not sp:
        continue
    s = max(sp, key=lambda t: t[1] - t[0])
    w_m = (s[1] - s[0]) * MPP
    print(f"  y={y:4d}  {s[0]:4d}-{s[1]:4d}   {w_m:6.0f}")
    best.append((abs(w_m - 800), y, s))

best.sort()
print("\n最接近 800 m 的走线:", best[:3])

d, y0, s = best[0]
x1, x2 = s
print(f"\n选定走线 y={y0}, 河宽 {(x2-x1)*MPP:.1f} m")
print(f"西岸点 pixel=({x1},{y0})  东岸点 pixel=({x2},{y0})")

def pix2lonlat(x, y):
    lon = LON0 + (x + 0.0) / W * (LON1 - LON0)
    # 纬度按 Web Mercator 反算
    n = 2 ** 16
    tx = 53329 + x / 256.0
    ty = 27470 + y / 256.0
    lon_m = tx / n * 360.0 - 180.0
    lat_m = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * ty / n))))
    return lon_m, lat_m


for name, (x, y) in [("西岸", (x1, y0)), ("东岸", (x2, y0))]:
    lo, la = pix2lonlat(x, y)
    print(f"  {name}: 经度 {lo:.6f}  纬度 {la:.6f}")
