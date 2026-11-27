# -*- coding: utf-8 -*-
"""在湘江卫星影像上绘制控制网图 (初始 / 方案2二次优化 / 方案1二次优化)"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
BASE = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"
IMG = os.path.join(BASE, "imagery", "siteA_z16.jpg")
MPP = 2.112

# ---- 桥位: QZ1 影像像素坐标与桥轴方向 ----
ORIGIN = (548.7, 1048.3)          # QZ1 像素位置
UX, UY = 0.9960, 0.0897           # X 轴方向(指向 QZ3), 像素系
VX, VY = -UY, UX                  # Y 轴方向(行进方向右侧)
CROP = (255, 825, 1030, 1255)     # left, top, right, bottom


def to_pix(X, Y):
    px = ORIGIN[0] + (X * UX + Y * VX) / MPP
    py = ORIGIN[1] + (X * UY + Y * VY) / MPP
    return px, py


cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

with open(os.path.join(BASE, "results_prec.json"), encoding="utf-8") as f:
    RP = json.load(f)

img = Image.open(IMG).convert("RGB")
crop_img = img.crop(CROP)
W_m = (CROP[2] - CROP[0]) * MPP
H_m = (CROP[3] - CROP[1]) * MPP
print(f"裁剪区域 {W_m:.0f} m × {H_m:.0f} m, 像素 {crop_img.size}")


def draw(ax, edges, dirs, title, axis_color="#1a5276"):
    ax.imshow(crop_img, extent=(CROP[0], CROP[2], CROP[3], CROP[1]))
    # 仅方向观测(虚线箭头)
    eset = {tuple(sorted(e)) for e in edges}
    for (_t, p, q) in dirs:
        if tuple(sorted((p, q))) in eset:
            continue
        x1, y1 = to_pix(*cnet.XY[p])
        x2, y2 = to_pix(*cnet.XY[q])
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.9,
                                    ls="--", shrinkA=4, shrinkB=4), zorder=6)
    # 实测边
    for (p, q) in edges:
        x1, y1 = to_pix(*cnet.XY[p])
        x2, y2 = to_pix(*cnet.XY[q])
        ax.plot([x1, x2], [y1, y2], "-", color="#f1c40f", lw=2.4, zorder=4,
                solid_capstyle="round")
        ax.plot([x1, x2], [y1, y2], "-", color=axis_color, lw=1.0, zorder=5)
    # 桥轴线
    x1, y1 = to_pix(-560, 0)
    x2, y2 = to_pix(880, 0)
    ax.plot([x1, x2], [y1, y2], ":", color="white", lw=1.6, zorder=3)
    ax.plot([x1, x2], [y1, y2], ":", color="#7d3c98", lw=1.0, zorder=4)
    # 控制点
    for p in cnet.PTS:
        x, y = to_pix(*cnet.XY[p])
        if p in ("QZ1", "QZ2", "QZ3"):
            ax.plot(x, y, "o", ms=8.5, mfc="#f5b041", mec="k", mew=1.0, zorder=9)
        elif p in ("QN1", "QN2"):
            ax.plot(x, y, "o", ms=8.0, mfc="#d7bde2", mec="k", mew=1.0, zorder=9)
        else:
            ax.plot(x, y, "o", ms=8.0, mfc="#2ecc71", mec="k", mew=1.0, zorder=9)
        dx, dy = {"QZ1": (-30, 12), "QZ2": (-30, -16), "QZ3": (10, -14),
                  "QN1": (-30, 12), "QN2": (-32, -14), "BX": (10, 8),
                  "BD": (10, -14), "NN": (-30, -16), "ND": (10, 6)}[p]
        ax.annotate(p, (x, y), textcoords="offset points", xytext=(dx, dy),
                    fontsize=8.6, fontweight="bold", color="white",
                    bbox=dict(boxstyle="round,pad=0.15", fc="black", alpha=0.55,
                              ec="none"), zorder=10)
    # 桥轴线标注
    xa, ya = to_pix(220, -34)
    ax.annotate("桥轴线（800 m）", (xa, ya), fontsize=8.0, color="white",
                zorder=10, rotation=-5,
                bbox=dict(boxstyle="round,pad=0.12", fc="#512e5f", alpha=0.65,
                          ec="none"))
    # 河流标注
    xr, yr = to_pix(400, -430)
    ax.annotate("湘　江", (xr, yr), fontsize=12, color="white", rotation=0,
                fontstyle="italic", zorder=10,
                bbox=dict(boxstyle="round,pad=0.2", fc="#1b4f72", alpha=0.55,
                          ec="none"))
    # 比例尺
    sb = 200.0 / MPP
    x0, y0 = CROP[0] + 25, CROP[3] - 35
    ax.plot([x0, x0 + sb], [y0, y0], "-", color="white", lw=5, zorder=10,
            solid_capstyle="butt")
    ax.plot([x0, x0 + sb], [y0, y0], "-", color="k", lw=2.5, zorder=11,
            solid_capstyle="butt")
    ax.text(x0 + sb / 2, y0 - 14, "200 m", ha="center", fontsize=8.5,
            color="white", zorder=11,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    # 指北针
    ax.annotate("", xy=(CROP[2] - 40, CROP[1] + 25),
                xytext=(CROP[2] - 40, CROP[1] + 95),
                arrowprops=dict(arrowstyle="-|>", color="white", lw=2.4), zorder=11)
    ax.annotate("", xy=(CROP[2] - 40, CROP[1] + 25),
                xytext=(CROP[2] - 40, CROP[1] + 95),
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2), zorder=12)
    ax.text(CROP[2] - 40, CROP[1] + 14, "N", ha="center", fontsize=10,
            fontweight="bold", color="white", zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    ax.set_xlim(CROP[0], CROP[2])
    ax.set_ylim(CROP[3], CROP[1])
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("k")
        s.set_linewidth(1.0)
    # 图例
    lx, ly = CROP[0] + 25, CROP[1] + 22
    ax.plot(lx, ly, "o", ms=8.5, mfc="#f5b041", mec="k", zorder=12)
    ax.text(lx + 14, ly + 4, "轴线点 QZ", fontsize=7.5, color="white", zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    ax.plot(lx + 95, ly, "o", ms=8.0, mfc="#2ecc71", mec="k", zorder=12)
    ax.text(lx + 108, ly + 4, "两岸控制点", fontsize=7.5, color="white",
            zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    ax.plot(lx + 190, ly, "o", ms=8.0, mfc="#d7bde2", mec="k", zorder=12)
    ax.text(lx + 203, ly + 4, "引桥点", fontsize=7.5, color="white", zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    ax.plot([lx + 258, lx + 290], [ly, ly], "-", color="#f1c40f", lw=2.4,
            zorder=12)
    ax.plot([lx + 258, lx + 290], [ly, ly], "-", color="#1a5276", lw=1.0,
            zorder=12)
    ax.text(lx + 295, ly + 4, "观测边（边+方向）", fontsize=7.5, color="white",
            zorder=12,
            bbox=dict(boxstyle="round,pad=0.1", fc="black", alpha=0.5, ec="none"))
    ax.set_title(title, fontsize=10.5)


PANELS = [
    ("（a）初始方案（全边角网，105 个观测）",
     sorted({(min(o[1], o[2]), max(o[1], o[2])) for o in cnet.build_obs(cnet.EDGES0)}),
     cnet.build_obs(cnet.EDGES0)),
    ("（b）方案 2（固定两点）二次优化后（51 个观测）",
     [tuple(e) for e in RP["方案2_二次优化"]["edges"]],
     [("F", *d) for d in RP["方案2_二次优化"]["dirs"]]),
    ("（c）方案 1（固定一点一方向）二次优化后（53 个观测）",
     [tuple(e) for e in RP["方案1_二次优化"]["edges"]],
     [("F", *d) for d in RP["方案1_二次优化"]["dirs"]]),
]

# ---- 三联图(纵向排列, 用于附图页) ----
fig, axes = plt.subplots(3, 1, figsize=(7.6, 9.6))
for ax, (t, e, d) in zip(axes, PANELS):
    draw(ax, e, d, t)
fig.suptitle("桥梁 GNSS 施工控制网 模拟优化设计 —— 控制网图（影像底图）",
             fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.965))
f3 = os.path.join(BASE, "控制网图（影像底图·三联）.png")
fig.savefig(f3, dpi=200, facecolor="white")
plt.close(fig)
print("saved", f3)

# ---- 单幅图(用于指导书 p29) ----
fig, ax = plt.subplots(figsize=(10.6, 5.9))
draw(ax, PANELS[0][1], PANELS[0][2], "")
fig.tight_layout()
f1 = os.path.join(BASE, "控制网图（影像底图）.png")
fig.savefig(f1, dpi=200, facecolor="white")
plt.close(fig)
print("saved", f1)
