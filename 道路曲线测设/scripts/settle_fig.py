# -*- coding: utf-8 -*-
"""建筑物沉降: 生成 沉降过程曲线图 与 观测路线示意图"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from settle_data import (SETTLE, MON, BENCH, LOOP, RING_W, ring_length,
                         ring_limit)   # noqa: E402

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\沉降测量成果"
os.makedirs(OUT, exist_ok=True)

# ================= 图1 沉降过程曲线 =================
fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2),
                         gridspec_kw={"width_ratios": [1.45, 1]})
ax = axes[0]
x = [1, 2, 3]
colors = {"P1": "#c0392b", "P2": "#2471a3", "P3": "#27ae60", "P4": "#8e44ad"}
marks = {"P1": "o", "P2": "s", "P3": "^", "P4": "D"}
for k in ["P1", "P2", "P3", "P4"]:
    d = SETTLE[k]
    ys = [0.0, d["d1"], d["cum"]]
    ax.plot(x, ys, "-", marker=marks[k], ms=6, lw=1.8, color=colors[k],
            label=f"{k}")
    dy = {"P1": 11, "P3": -16, "P2": -15, "P4": -15}[k]
    for xx, yy in zip(x, ys):
        if xx == 1 and yy == 0.0:
            continue
        ax.annotate(f"{yy:+.2f}", (xx, yy), textcoords="offset points",
                    xytext=(0, dy if yy >= 0 or k == "P3" else -15),
                    ha="center", fontsize=8, color=colors[k])
ax.axhline(0, color="0.4", lw=0.9, ls="-")
ax.set_xticks(x)
ax.set_xticklabels(["第一期\n(第 0 天)", "第二期\n(相隔 7 天)", "第三期\n(相隔 14 天)"])
ax.set_ylabel("累积沉降量（mm）")
ax.set_title("变形监测点累积沉降过程曲线", fontsize=12)
ax.grid(ls=":", color="0.75")
ax.legend(loc="lower left", ncol=2, fontsize=9, framealpha=0.95)
ax.set_ylim(-1.15, 0.55)

ax2 = axes[1]
import numpy as np
w = 0.19
base = np.arange(2)
for i, k in enumerate(["P1", "P2", "P3", "P4"]):
    d = SETTLE[k]
    ax2.bar(base + (i - 1.5) * w, [d["d1"], d["d2"]], width=w,
            color=colors[k], label=k, edgecolor="k", linewidth=0.5)
ax2.axhline(0, color="0.4", lw=0.9)
ax2.set_xticks(base)
ax2.set_xticklabels(["第一周\n(2期-1期)", "第二周\n(3期-2期)"])
ax2.set_ylabel("分期沉降量（mm）")
ax2.set_title("各周沉降量对比", fontsize=12)
ax2.grid(ls=":", axis="y", color="0.75")
ax2.legend(fontsize=9, ncol=2)
fig.tight_layout()
f1 = os.path.join(OUT, "沉降过程曲线图.png")
fig.savefig(f1, dpi=220, facecolor="white")
plt.close(fig)
print("saved", f1)

# ================= 图2 观测路线示意图 =================
AB, BC, CA = 367.190, 93.300, 417.923
xc = (AB ** 2 + CA ** 2 - BC ** 2) / (2 * AB)
yc = math.sqrt(max(CA ** 2 - xc ** 2, 1.0))
A = (0.0, 0.0)
B = (AB, 0.0)
C = (xc, yc)

# 房角沿 A→B 的示意位置(按往测站号估算)
P_frac = {"P4": 157 / AB, "P3": 199 / AB, "P2": 241 / AB, "P1": 283 / AB}
P = {k: (AB * f, 0.0) for k, f in P_frac.items()}

fig, ax = plt.subplots(figsize=(11.6, 7.0))
# 环线
ax.plot([A[0], B[0], C[0], A[0]], [A[1], B[1], C[1], A[1]], "-",
        color="#2471a3", lw=2.0, zorder=2)
# 往返方向箭头
def arrow(p, q, frac0=0.12, frac1=0.32, color="#2471a3", ls="-"):
    px = p[0] + (q[0] - p[0]) * frac0, p[1] + (q[1] - p[1]) * frac0
    qx = p[0] + (q[0] - p[0]) * frac1, p[1] + (q[1] - p[1]) * frac1
    ax.annotate("", xy=qx, xytext=px,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                                linestyle=ls))

arrow(A, B, 0.05, 0.20)
arrow(B, C, 0.25, 0.55)
ax.annotate("", xy=(A[0] + (C[0] - A[0]) * 0.30, A[1] + (C[1] - A[1]) * 0.30),
            xytext=(A[0] + (C[0] - A[0]) * 0.50, A[1] + (C[1] - A[1]) * 0.50),
            arrowprops=dict(arrowstyle="-|>", color="#e67e22", lw=1.6))
ax.text(A[0] + (C[0] - A[0]) * 0.36, A[1] + (C[1] - A[1]) * 0.36 + 8,
        "返测 C→A（20 站）", color="#e67e22", fontsize=9, rotation=0)
ax.text(AB * 0.42, -16, "往测 A→B（含 4 个房角）", color="#2471a3",
        fontsize=9)
ax.text(B[0] + 8, B[1] + yc * 0.28, "往测 B→C（22 站）", color="#2471a3",
        fontsize=9, rotation=62)

# 边标注
ax.text(AB / 2, 10, f"A→B  {AB:.3f} m", ha="center", fontsize=9, color="#1f618d")
ax.text((B[0] + C[0]) / 2 + 12, (B[1] + C[1]) / 2 + 6,
        f"B→C\n{BC:.3f} m", fontsize=9, color="#1f618d")
ax.text((A[0] + C[0]) / 2 - 78, (A[1] + C[1]) / 2 + 8,
        f"C→A  {CA:.3f} m", fontsize=9, color="#1f618d")

# 点
ax.plot(*A, "^", ms=13, mfc="#f1c40f", mec="k", mew=1.0, zorder=6)
ax.plot(*B, "o", ms=11, mfc="#2ecc71", mec="k", mew=1.0, zorder=6)
ax.plot(*C, "o", ms=11, mfc="#2ecc71", mec="k", mew=1.0, zorder=6)
for k, p in P.items():
    ax.plot(*p, "s", ms=9, mfc="#e74c3c", mec="k", mew=0.8, zorder=6)
    ax.annotate(k, p, textcoords="offset points", xytext=(0, -20),
                ha="center", fontsize=10, fontweight="bold", color="#922b21")

# 房屋示意
hb = {"P4": 46, "P3": 62, "P2": 58, "P1": 44}
xs = [P[k][0] for k in P]
ax.add_patch(Rectangle((min(xs) - 26, 16), max(xs) - min(xs) + 52, 42,
                       fc="#f9e79f", ec="#b7950b", lw=1.4, alpha=0.75,
                       zorder=1))
ax.text(sum(xs) / 4, 62, "被监测房屋（4 个房角 P1～P4）", ha="center",
        fontsize=9, color="#7d6608")

ax.annotate("A（已知基准点，79.568 m）", A, textcoords="offset points",
            xytext=(-30, 26), fontsize=10, fontweight="bold")
ax.annotate("B（基准点）", B, textcoords="offset points", xytext=(16, 16),
            fontsize=10, fontweight="bold")
ax.annotate("C（基准点）", C, textcoords="offset points", xytext=(-10, 18),
            fontsize=10, fontweight="bold")

ax.set_title("建筑物沉降观测点位布设与观测路线示意图", fontsize=13)
ax.set_xlabel("距离（m，示意，非严格比例）")
ax.grid(ls=":", color="0.85")
ax.set_aspect("equal", adjustable="datalim")
ax.set_xlim(-70, max(xc, AB) + 90)
ax.set_ylim(-45, yc + 90)
# 比例尺
x0, x1 = ax.get_xlim()
y0, y1 = ax.get_ylim()
fr = 50.0 / (x1 - x0)
ax.plot([x0 + 0.06 * (x1 - x0), x0 + 0.06 * (x1 - x0) + fr], [y0 + 0.05 * (y1 - y0)] * 2,
        "-", color="k", lw=3, solid_capstyle="butt")
ax.text(x0 + 0.06 * (x1 - x0) + fr / 2, y0 + 0.065 * (y1 - y0), "50 m",
        ha="center", fontsize=8)
fig.tight_layout()
f2 = os.path.join(OUT, "观测路线示意图.png")
fig.savefig(f2, dpi=220, facecolor="white")
plt.close(fig)
print("saved", f2)
