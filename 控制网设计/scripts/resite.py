# -*- coding: utf-8 -*-
"""重新选址: 河道从 QZ1-QZ2 之间穿过, 9 点全部落在陆地/道路上
输出 resite.json 供绘图脚本使用"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
BASE = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"
IMG = os.path.join(BASE, "imagery", "siteD_z16.jpg")
MPP = 2.112
LON0, LON1 = 112.862549, 112.895508
LAT_TOP, LAT_BOT = 27.858504, 27.829361

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

im = Image.open(IMG).convert("RGB")
a = np.asarray(im).astype(np.int16)
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
H, W = R.shape

water = (R < 92) & (G < 122) & (B < 108) & (G >= R - 6)
veg = (G > R + 14) & (G > B + 14) & (G > 60)
bright = (R + G + B) / 3.0
pen = np.zeros((H, W), dtype=np.float32)
pen[water] = 5.0          # 水面: 绝对不行
pen[veg] = 1.0            # 植被: 尽量避开
pen[bright > 150] = 1.6   # 房屋: 避开


def spans(row):
    m = water[row]
    out, start = [], None
    for x in range(W):
        if m[x] and start is None:
            start = x
        elif not m[x] and start is not None:
            if x - start > 20:
                out.append((start, x - 1))
            start = None
    if start is not None and W - start > 20:
        out.append((start, W - 1))
    return out


def sample(x, y, rad=2):
    xi, yi = int(round(x)), int(round(y))
    if not (rad <= xi < W - rad and rad <= yi < H - rad):
        return 99.0
    return float(pen[yi - rad:yi + rad + 1, xi - rad:xi + rad + 1].mean())


cands = []
for y in range(60, H - 60, 3):
    for (x1, x2) in spans(y):
        wm = (x2 - x1) * MPP
        if not (330 <= wm <= 450):
            continue
        # QZ1 放在区间北/东侧边缘外 8 px, QZ2 在另一侧
        for flip in (0, 1):
            ex1, ex2 = (x2, x1) if flip else (x1, x2)
            ox = ex1 + (8 if flip == 0 else -8)
            oy = y
            th = 0.0 if flip == 0 else math.pi
            ux, uy = math.cos(th), math.sin(th)
            vx, vy = -uy, ux
            tot, ok = 0.0, True
            pts = {}
            for p, (X, Y) in cnet.XY.items():
                x = ox + (X * ux + Y * vx) / MPP
                yy = oy + (X * uy + Y * vy) / MPP
                pts[p] = (x, yy)
                s = sample(x, yy)
                if s >= 50:
                    ok = False
                tot += s
            if ok:
                cands.append((tot, y, x1, x2, flip, ox, oy, th, pts))

cands.sort(key=lambda c: c[0])
print(f"候选 {len(cands)} 个")
for c in cands[:8]:
    tot, y, x1, x2, flip, ox, oy, th, pts = c
    print(f"  总分 {tot:5.2f}  y={y} 河道 {x1}-{x2} "
          f"({(x2-x1)*MPP:.0f} m) flip={flip} 原点=({ox},{oy})")

if not cands:
    print("没有满足全部点在陆地的候选, 放宽条件")
    sys.exit(1)

tot, y, x1, x2, flip, ox, oy, th, pts = cands[0]
print("\n选中:")
for p in cnet.PTS:
    x, yy = pts[p]
    lo = LON0 + x / W * (LON1 - LON0)
    la = LAT_TOP - yy / H * (LAT_TOP - LAT_BOT)
    print(f"  {p:4s} pixel=({x:7.1f},{yy:7.1f}) 得分={sample(x,yy):.2f} "
          f"经纬度=({lo:.5f},{la:.5f})")

info = dict(image="siteD_z16.jpg", mpp=MPP,
            lon0=LON0, lon1=LON1, lat_top=LAT_TOP, lat_bot=LAT_BOT,
            origin=[ox, oy], angle_rad=th, river=[x1, y, x2],
            width_m=(x2 - x1) * MPP)
with open(os.path.join(BASE, "resite.json"), "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
print("\nsaved resite.json", info)
