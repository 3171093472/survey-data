# -*- coding: utf-8 -*-
"""在湘江昭山段卫星影像上绘制控制网图
(a) 初始全边角网 (b) 方案2二次优化 (c) 方案1二次优化
桥位: QZ1(934,528) 像素, 桥轴方向 150 度; QZ1/QZ2 分居两岸, 9 点均在陆地
"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
BASE = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"
IMG = os.path.join(BASE, "imagery", "siteG_z16.jpg")
MPP = 2.112
ORIGIN = (934.0, 528.0)
TH = math.radians(150.0)
UX, UY = math.cos(TH), math.sin(TH)
VX, VY = -UY, UX
CROP = (400, 230, 1300, 960)


def to_pix(X, Y):
    return (ORIGIN[0] + (X * UX + Y * VX) / MPP,
            ORIGIN[1] + (X * UY + Y * VY) / MPP)


cnet.XY.clear()
cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

with open(os.path.join(BASE, "results_prec.json"), encoding="utf-8") as f:
    RP = json.load(f)

img = Image.open(IMG).convert("RGB")
crop_img = img.crop(CROP)
print("crop", crop_img.size, "=",
      f"{(CROP[2]-CROP[0])*MPP:.0f} m x {(CROP[3]-CROP[1])*MPP:.0f} m")


def draw(ax, edges, dirs, title, lw=2.2):
    ax.imshow(crop_img, extent=(CROP[0], CROP[2], CROP[3], CROP[1]))
    eset = {tuple(sorted(e)) for e in edges}
    for (_t, p, q) in dirs:
        if tuple(sorted((p, q))) in eset:
            continue
        x1, y1 = to_pix(*cnet.XY[p])
        x2, y2 = to_pix(*cnet.XY[q])
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9,
                                    ls="--", shrinkA=4, shrinkB=4), zorder=6)
    for (p, q) in edges:
        x1, y1 = to_pix(*cnet.XY[p])
        x2, y2 = to_pix(*cnet.XY[q])
        ax.plot([x1, x2], [y1, y2], "-", color="#f1c40f", lw=lw + 1.3,
                zorder=4, solid_capstyle="round")
        ax.plot([x1, x2], [y1, y2], "-", color="#1a5276", lw=0.9, zorder=5)
    x1, y1 = to_pix(-540, 0)
    x2, y2 = to_pix(830, 0)
    ax.plot([x1, x2], [y1, y2], ":", color="white", lw=2.0, zorder=3)
    ax.plot([x1, x2], [y1, y2], ":", color="#7d3c98", lw=1.1, zorder=4)
    for p in cnet.PTS:
        x, y = to_pix(*cnet.XY[p])
        if p in ("QZ1", "QZ2", "QZ3"):
            ax.plot(x, y, "o", ms=9.5, mfc="#f5b041", mec="k", mew=1.1,
                    zorder=9)
        elif p in ("QN1", "QN2"):
            ax.plot(x, y, "o", ms=9.0, mfc="#d7bde2", mec="k", mew=1.1,
                    zorder=9)
        else:
            ax.plot(x, y, "o", ms=9.0, mfc="#2ecc71", mec="k", mew=1.1,
                    zorder=9)
        dx, dy = {"QZ1": (12, -14), "QZ2": (-38, 8), "QZ3": (12, 8),
                  "QN1": (12, -14), "QN2": (12, 8), "BX": (12, 6),
                  "BD": (12, 8), "NN": (-40, 8), "ND": (-40, 8)}[p]
        ax.annotate(p, (x, y), textcoords="offset points", xytext=(dx, dy),
                    fontsize=9.5, fontweight="bold", color="white",
                    bbox=dict(boxstyle="round,pad=0.16", fc="black",
                              alpha=0.62, ec="none"), zorder=10)
    xa, ya = to_pix(200, -46)
    ax.annotate("桥轴线(800 m)", (xa, ya), fontsize=8.5, color="white",
                rotation=math.degrees(math.atan2(-UY, -UX)), zorder=10,
                bbox=dict(boxstyle="round,pad=0.14", fc="#512e5f",
                          alpha=0.7, ec="none"))
    xr, yr = to_pix(140, 130)
    ax.annotate("湘　江", (xr, yr), fontsize=13, color="white",
                fontstyle="italic", zorder=10,
                bbox=dict(boxstyle="round,pad=0.2", fc="#1b4f72",
                          alpha=0.55, ec="none"))
    sb = 200.0 / MPP
    x0, y0 = CROP[0] + 30, CROP[3] - 40
    ax.plot([x0, x0 + sb], [y0, y0], "-", color="white", lw=6, zorder=10,
            solid_capstyle="butt")
    ax.plot([x0, x0 + sb], [y0, y0], "-", color="k", lw=3, zorder=11,
            solid_capstyle="butt")
    ax.text(x0 + sb / 2, y0 - 16, "200 m", ha="center", fontsize=9,
            color="white", zorder=11,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.55,
                      ec="none"))
    ax.annotate("", xy=(CROP[2] - 45, CROP[1] + 28),
                xytext=(CROP[2] - 45, CROP[1] + 108),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2.6),
                zorder=11)
    ax.annotate("", xy=(CROP[2] - 45, CROP[1] + 28),
                xytext=(CROP[2] - 45, CROP[1] + 108),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2),
                zorder=12)
    ax.text(CROP[2] - 45, CROP[1] + 16, "N", ha="center", fontsize=11,
            fontweight="bold", color="white", zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.55,
                      ec="none"))
    lx, ly = CROP[0] + 30, CROP[1] + 28
    ax.plot(lx, ly, "o", ms=9, mfc="#f5b041", mec="k", zorder=12)
    ax.text(lx + 16, ly + 4, "轴线点 QZ", fontsize=8, color="white",
            zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.55,
                      ec="none"))
    ax.plot(lx + 108, ly, "o", ms=8.5, mfc="#2ecc71", mec="k", zorder=12)
    ax.text(lx + 122, ly + 4, "两岸控制点", fontsize=8, color="white",
            zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.55,
                      ec="none"))
    ax.plot(lx + 215, ly, "o", ms=8.5, mfc="#d7bde2", mec="k", zorder=12)
    ax.text(lx + 229, ly + 4, "引桥点", fontsize=8, color="white", zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.55,
                      ec="none"))
    ax.set_xlim(CROP[0], CROP[2])
    ax.set_ylim(CROP[3], CROP[1])
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("k")
        s.set_linewidth(1.0)
    if title:
        ax.set_title(title, fontsize=11)


PANELS = [
    ("（a）初始方案（全边角网，105 个观测）",
     sorted({(min(o[1], o[2]), max(o[1], o[2]))
             for o in cnet.build_obs(cnet.EDGES0)}),
     cnet.build_obs(cnet.EDGES0)),
    ("（b）方案 2（固定两点）二次优化后（51 个观测）",
     [tuple(e) for e in RP["方案2_二次优化"]["edges"]],
     [("F", *d) for d in RP["方案2_二次优化"]["dirs"]]),
    ("（c）方案 1（固定一点一方向）二次优化后（53 个观测）",
     [tuple(e) for e in RP["方案1_二次优化"]["edges"]],
     [("F", *d) for d in RP["方案1_二次优化"]["dirs"]]),
]

fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.0))
for ax, (t, e, d) in zip(axes, PANELS):
    draw(ax, e, d, t)
fig.suptitle("桥梁 GNSS 施工控制网 模拟优化设计 —— 控制网图（湘江影像底图）",
             fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.93))
f3 = os.path.join(BASE, "控制网图（影像底图·三联）.png")
fig.savefig(f3, dpi=210, facecolor="white")
plt.close(fig)
print("saved", f3)

fig, ax = plt.subplots(figsize=(9.2, 7.6))
draw(ax, PANELS[0][1], PANELS[0][2], "")
fig.tight_layout()
f1 = os.path.join(BASE, "控制网图（影像底图）.png")
fig.savefig(f1, dpi=220, facecolor="white")
plt.close(fig)
print("saved", f1)
