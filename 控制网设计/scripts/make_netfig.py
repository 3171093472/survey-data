# -*- coding: utf-8 -*-
"""控制网图: (a) 初始全边角网 (b) 方案2 二次优化 (c) 方案1 二次优化"""
import json
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

with open(os.path.join(OUT, "results_prec.json"), encoding="utf-8") as f:
    RES = json.load(f)

panels = [
    ("（a）初始方案（全边角网，105 个观测）",
     sorted({(min(o[1], o[2]), max(o[1], o[2])) for o in cnet.build_obs(cnet.EDGES0)}),
     cnet.build_obs(cnet.EDGES0)),
    ("（b）方案 2（固定两点）二次优化后（51 个观测）",
     [tuple(e) for e in RES["方案2_二次优化"]["edges"]],
     [("F", *d) for d in RES["方案2_二次优化"]["dirs"]]),
    ("（c）方案 1（固定一点一方向）二次优化后（53 个观测）",
     [tuple(e) for e in RES["方案1_二次优化"]["edges"]],
     [("F", *d) for d in RES["方案1_二次优化"]["dirs"]]),
]

fig, axes = plt.subplots(1, 3, figsize=(13.2, 6.6))
for ax, (title, edges, dirs) in zip(axes, panels):
    # 边长(实线)
    for (p, q) in edges:
        x1, y1 = cnet.XY[p]
        x2, y2 = cnet.XY[q]
        ax.plot([y1, y2], [x1, x2], "-", color="#2471a3", lw=0.75, zorder=2)
    # 仅方向观测(虚线)
    obs_dirs = {(o[1], o[2]) for o in dirs}
    edge_set = {tuple(sorted(e)) for e in edges}
    for (p, q) in obs_dirs:
        if tuple(sorted((p, q))) in edge_set:
            continue
        x1, y1 = cnet.XY[p]
        x2, y2 = cnet.XY[q]
        ax.annotate("", xy=(y2, x2), xytext=(y1, x1),
                    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=0.7,
                                    ls="--", shrinkA=3, shrinkB=3))
    # 点
    for p in cnet.PTS:
        x, y = cnet.XY[p]
        is_axis = p.startswith("QZ") or p.startswith("QN")
        ax.plot(y, x, "o", ms=8.5 if is_axis else 7.5,
                mfc="#f5b041" if is_axis else "#2ecc71",
                mec="k", mew=0.8, zorder=5)
    # 标注
    off = {"QZ3": (8, 8), "QZ2": (-26, 6), "QZ1": (-26, 4), "QN1": (8, -12),
           "QN2": (-16, -16), "BX": (-24, 4), "BD": (8, 4), "NN": (8, -12),
           "ND": (8, 4)}
    for p in cnet.PTS:
        x, y = cnet.XY[p]
        dx, dy = off.get(p, (6, 4))
        ax.annotate(p, (y, x), textcoords="offset points", xytext=(dx, dy),
                    fontsize=8.6, fontweight="bold")
    # 桥轴线
    ax.plot([0, 0], [0, 800], ":", color="0.5", lw=1.0, zorder=1)
    ax.set_title(title, fontsize=9.5)
    ax.set_aspect("equal")
    ax.grid(ls=":", color="0.9")
    ax.tick_params(labelsize=7)
    ax.set_xlabel("Y（m，东）", fontsize=8)
    ax.set_ylabel("X（m，北）", fontsize=8)

fig.suptitle("桥梁 GNSS 施工控制网 模拟优化设计 —— 控制网图", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, 0.95))
f1 = os.path.join(OUT, "控制网图.png")
fig.savefig(f1, dpi=220, facecolor="white")
print("saved", f1)
