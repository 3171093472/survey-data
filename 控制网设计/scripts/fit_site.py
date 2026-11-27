# -*- coding: utf-8 -*-
"""在影像上搜索控制网布设位置: 使 9 个控制点尽量落在道路/裸地, 避开水面与草地"""
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"
IMG = os.path.join(BASE, "imagery", "siteA_z16.jpg")
MPP = 2.112

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

im = Image.open(IMG).convert("RGB")
a = np.asarray(im).astype(np.int16)
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
H, W = R.shape

water = (R < 88) & (G < 118) & (B < 105) & (G >= R - 5)
veg = (G > R + 14) & (G > B + 14) & (G > 60)
bright = (R + G + B) / 3.0
building = bright > 155
pen = np.zeros((H, W), dtype=np.float32)
pen[water] = 1.0
pen[veg] = 1.0
pen[building] = 0.25


def sample_pen(x, y, rad=3):
    xi, yi = int(round(x)), int(round(y))
    x0, x1 = max(0, xi - rad), min(W, xi + rad + 1)
    y0, y1 = max(0, yi - rad), min(H, yi + rad + 1)
    return float(pen[y0:y1, x0:x1].mean()), xi, yi


def place(ox, oy, th):
    """th: 桥轴 X 方向在像素系中的角度(弧度, 顺时针为正)"""
    ux, uy = math.cos(th), math.sin(th)
    vx, vy = -uy, ux
    out = {}
    for p, (X, Y) in cnet.XY.items():
        out[p] = (ox + (X * ux + Y * vx) / MPP, oy + (X * uy + Y * vy) / MPP)
    return out


def score(pts):
    tot = 0.0
    for p, (x, y) in pts.items():
        if not (0 <= x < W and 0 <= y < H):
            return 99.0
        s, _, _ = sample_pen(x, y)
        tot += s
    return tot


best = None
for ox in range(500, 611, 5):
    for oy in range(950, 1106, 5):
        for deg in range(-20, 21, 4):
            pts = place(ox, oy, math.radians(deg))
            sc = score(pts)
            if best is None or sc < best[0]:
                best = (sc, ox, oy, deg, pts)

sc, ox, oy, deg, pts = best
print(f"最优: 原点像素=({ox},{oy}) 桥轴角={deg}°  惩罚和={sc:.3f}")
for p in cnet.PTS:
    x, y = pts[p]
    s, _, _ = sample_pen(x, y)
    lo, la = 0, 0
    print(f"  {p:4s} pixel=({x:7.1f},{y:7.1f})  草地/水面比例={s:.2f}")

# 输出可供绘图脚本使用的参数
print(f"\nORIGIN = ({ox}, {oy})  ANGLE_DEG = {deg}")
