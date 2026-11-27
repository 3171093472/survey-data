# -*- coding: utf-8 -*-
"""在 siteG(昭山段) 搜索桥位: QZ1/QZ2 均在陆地、中点在水面、其余 7 点均不在水面
保持原设计坐标(QZ2=400)不变"""
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

cnet.XY.clear()
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
pen[water] = 30.0
pen[veg] = 1.0
pen[bright > 150] = 2.0


def wy(x, y):
    xi, yi = int(round(x)), int(round(y))
    if not (0 <= xi < W and 0 <= yi < H):
        return None
    return bool(water[yi, xi])


def sc(x, y, rad=3):
    xi, yi = int(round(x)), int(round(y))
    if not (rad <= xi < W - rad and rad <= yi < H - rad):
        return 99.0
    return float(pen[yi - rad:yi + rad + 1, xi - rad:xi + rad + 1].mean())


MPP = CFG["mpp"]
results = []
for deg in range(0, 180, 5):
    th = math.radians(deg)
    ux, uy = math.cos(th), math.sin(th)
    vx, vy = -uy, ux
    for gx in range(150, W - 150, 14):
        for gy in range(150, H - 150, 14):
            # QZ1 在陆地, 200 m 处在水面, QZ2(400 m) 在陆地
            mid = (gx + 200 / MPP * ux, gy + 200 / MPP * uy)
            q2 = (gx + 400 / MPP * ux, gy + 400 / MPP * uy)
            w0, wm, w2 = wy(gx, gy), wy(*mid), wy(*q2)
            if w0 is None or wm is None or w2 is None:
                continue
            if w0 or w2 or not wm:
                continue
            pts, tot, ok = {}, 0.0, True
            for p, (X, Y) in cnet.XY.items():
                x = gx + (X * ux + Y * vx) / MPP
                y = gy + (X * uy + Y * vy) / MPP
                pts[p] = (x, y)
                s = sc(x, y)
                if s >= 15:
                    ok = False
                    break
                tot += s
            if ok:
                results.append((tot, deg, gx, gy, pts))

results.sort(key=lambda t: t[0])
print(f"候选 {len(results)}")
for r in results[:6]:
    print(f"  总分 {r[0]:5.2f} 角度={r[1]}° 原点=({r[2]},{r[3]})")
if not results:
    sys.exit("无候选")

tot, deg, gx, gy, pts = results[0]
print("\n选定: 角度", deg, "原点", (gx, gy))
for p in cnet.PTS:
    x, y = pts[p]
    lo = CFG["lon0"] + x / W * (CFG["lon1"] - CFG["lon0"])
    la = CFG["lat_top"] - y / H * (CFG["lat_top"] - CFG["lat_bot"])
    print(f"  {p:4s} ({x:7.1f},{y:7.1f}) 得分={sc(x,y):.2f} "
          f"({lo:.5f},{la:.5f})")
info = dict(image=CFG["image"], mpp=MPP, width=W, height=H,
            origin=[gx, gy], angle_deg=deg,
            lon0=CFG["lon0"], lon1=CFG["lon1"],
            lat_top=CFG["lat_top"], lat_bot=CFG["lat_bot"])
with open(os.path.join(BASE, "resite.json"), "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
print("saved resite.json", info)
