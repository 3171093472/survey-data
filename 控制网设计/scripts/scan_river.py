# -*- coding: utf-8 -*-
"""在 z14 大范围影像上扫描湘江各段河宽, 找 300~430 m 的窄河段"""
import os
import sys

import numpy as np
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\imagery"
IMG = os.path.join(BASE, "m_z14.jpg")
MPP = 8.45
LON0, LON1 = 112.873535, 113.005371
LAT0, LAT1 = 27.819645, 27.916767

im = Image.open(IMG).convert("RGB")
a = np.asarray(im).astype(np.int16)
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
H, W = R.shape
water = (R < 88) & (G < 118) & (B < 105) & (G >= R - 5)


def spans(row):
    m = water[row]
    out, start = [], None
    for x in range(W):
        if m[x] and start is None:
            start = x
        elif not m[x] and start is not None:
            if x - start > 15:
                out.append((start, x - 1))
            start = None
    if start is not None and W - start > 15:
        out.append((start, W - 1))
    return out


cands = []
for y in range(0, H, 8):
    for (x1, x2) in spans(y):
        wm = (x2 - x1) * MPP
        if 300 <= wm <= 430:
            lon = LON0 + (x1 + x2) / 2 / W * (LON1 - LON0)
            # 纬度: 像素 y 从上到下对应 lat1 -> lat0 (近似线性)
            lat = LAT1 - (y / H) * (LAT1 - LAT0)
            cands.append((wm, y, x1, x2, lon, lat))
print(f"找到 {len(cands)} 个 300~430 m 河宽断面")
for c in cands[::max(1, len(cands) // 25)]:
    print(f"  河宽 {c[0]:5.0f} m  y={c[1]:4d}  x {c[2]}-{c[3]}  "
          f"中心经纬度 ({c[4]:.5f}, {c[5]:.5f})")
