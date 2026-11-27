# -*- coding: utf-8 -*-
"""在 siteG 影像上选址: 河道从 QZ1-QZ2 之间穿过, 9 点全部在陆地
用法: py resite2.py
"""
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
CFG = dict(image="siteG_z16.jpg", mpp=2.112,
           lon0=112.966919, lon1=112.999878,
           lat_top=27.955591, lat_bot=27.926474)

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

im = Image.open(os.path.join(BASE, "imagery", CFG["image"])).convert("RGB")
a = np.asarray(im).astype(np.int16)
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
H, W = R.shape
water = (R < 92) & (G < 122) & (B < 108) & (G >= R - 6)
veg = (G > R + 14) & (G > B + 14) & (G > 60)
bright = (R + G + B) / 3.0
pen = np.zeros((H, W), dtype=np.float32)
pen[water] = 20.0          # 水面绝对禁止
pen[veg] = 1.0
pen[bright > 150] = 2.0    # 房屋


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


def sc(x, y, rad=3):
    xi, yi = int(round(x)), int(round(y))
    if not (rad <= xi < W - rad and rad <= yi < H - rad):
        return 99.0
    return float(pen[yi - rad:yi + rad + 1, xi - rad:xi + rad + 1].mean())


best = []
for y in range(60, H - 60, 3):
    for (x1, x2) in spans(y):
        wm = (x2 - x1) * CFG["mpp"]
        if not (330 <= wm <= 450):
            continue
        for flip in (0, 1):
            # flip=0: QZ1 在左岸(x1 外侧), 桥轴指向 +x
            # flip=1: QZ1 在右岸(x2 外侧), 桥轴指向 -x
            ox = x1 - 10 if flip == 0 else x2 + 10
            th = 0.0 if flip == 0 else math.pi
            ux, uy = math.cos(th), math.sin(th)
            vx, vy = -uy, ux
            pts, tot, ok, nwater = {}, 0.0, True, 0
            for p, (X, Y) in cnet.XY.items():
                x = ox + (X * ux + Y * vx) / CFG["mpp"]
                yy = y + (X * uy + Y * vy) / CFG["mpp"]
                pts[p] = (x, yy)
                s = sc(x, yy)
                if s >= 15:
                    ok = False
                tot += s
            if ok:
                best.append((tot, y, x1, x2, flip, ox, th, pts))

best.sort(key=lambda c: c[0])
print(f"候选 {len(best)}")
for c in best[:6]:
    tot, y, x1, x2, flip, ox, th, pts = c
    print(f"  总分 {tot:5.2f} y={y} 河道 {x1}-{x2} ({(x2-x1)*CFG['mpp']:.0f} m) "
          f"flip={flip} 原点=({ox},{y})")
if not best:
    sys.exit("无候选")

tot, y, x1, x2, flip, ox, th, pts = best[0]
print("\n选定:")
for p in cnet.PTS:
    x, yy = pts[p]
    lo = CFG["lon0"] + x / W * (CFG["lon1"] - CFG["lon0"])
    la = CFG["lat_top"] - yy / H * (CFG["lat_top"] - CFG["lat_bot"])
    print(f"  {p:4s} ({x:7.1f},{yy:7.1f}) 得分={sc(x,yy):.2f} "
          f"({lo:.5f},{la:.5f})")
info = dict(CFG, origin=[ox, y], angle_rad=th, river=[x1, y, x2],
            width_m=(x2 - x1) * CFG["mpp"])
info.pop("mpp", None)
info["mpp"] = CFG["mpp"]
with open(os.path.join(BASE, "resite.json"), "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
print("saved resite.json")
