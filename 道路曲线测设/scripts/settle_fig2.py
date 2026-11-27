# -*- coding: utf-8 -*-
"""建筑物沉降: 观测路线示意图(重绘)"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

AB, BC, CA = 367.190, 93.300, 417.923
xc = (AB ** 2 + CA ** 2 - BC ** 2) / (2 * AB)
yc = math.sqrt(max(CA ** 2 - xc ** 2, 1.0))
A, B, C = (0.0, 0.0), (AB, 0.0), (xc, yc)
P_frac = {"P4": 157 / AB, "P3": 199 / AB, "P2": 241 / AB, "P1": 283 / AB}
P = {k: (AB * f, 0.0) for k, f in P_frac.items()}

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\沉降测量成果"
os.makedirs(OUT, exist_ok=True)

fig, ax = plt.subplots(figsize=(11.8, 6.6))
# 房屋
xs = [P[k][0] for k in P]
ax.add_patch(Rectangle((min(xs) - 30, -88), max(xs) - min(xs) + 60, 55,
                       fc="#fcf3cf", ec="#b7950b", lw=1.4, alpha=0.9,
                       zorder=1))
ax.text(sum(xs) / 4, -46, "被监测房屋（P1～P4 为房屋四角）", ha="center",
        va="center", fontsize=9.5, color="#7d6608")
for k, p in P.items():
    ax.plot([p[0], p[0]], [0, -33], ls=":", color="#b7950b", lw=0.9, zorder=1)

# 往测环路 A→B→C
ax.plot([A[0], B[0], C[0]], [A[1], B[1], C[1]], "-", color="#2471a3", lw=2.2,
        zorder=3, label="往测路线 A→B→C（22 站）")
# 返测 C→A
ax.plot([C[0], A[0]], [C[1], A[1]], "--", color="#e67e22", lw=2.0, zorder=2,
        label="返测路线 C→A（20 站）")

for p, q, f0, f1 in [(A, B, 0.20, 0.34), (B, C, 0.22, 0.55)]:
    ax.annotate("", xy=(p[0] + (q[0] - p[0]) * f1, p[1] + (q[1] - p[1]) * f1),
                xytext=(p[0] + (q[0] - p[0]) * f0, p[1] + (q[1] - p[1]) * f0),
                arrowprops=dict(arrowstyle="-|>", color="#2471a3", lw=1.8))
ax.annotate("", xy=(A[0] + (C[0] - A[0]) * 0.28, A[1] + (C[1] - A[1]) * 0.28),
            xytext=(A[0] + (C[0] - A[0]) * 0.44, A[1] + (C[1] - A[1]) * 0.44),
            arrowprops=dict(arrowstyle="-|>", color="#e67e22", lw=1.8))

# 边长标注(沿边法向偏移)
ax.text(AB * 0.5, -16, f"A→B = {AB:.3f} m", ha="center", va="top", fontsize=9.5,
        color="#1f618d")
mid = ((B[0] + C[0]) / 2, (B[1] + C[1]) / 2)
ang = math.degrees(math.atan2(C[1] - B[1], C[0] - B[0]))
ax.text(mid[0] - 12, mid[1] + 6, f"B→C\n{BC:.3f} m", ha="right", va="center",
        fontsize=9.5, color="#1f618d", rotation=ang)
mid2 = ((A[0] + C[0]) / 2, (A[1] + C[1]) / 2)
ang2 = math.degrees(math.atan2(C[1] - A[1], C[0] - A[0]))
ax.text(mid2[0] - 5, mid2[1] + 16, f"C→A = {CA:.3f} m", ha="center",
        va="bottom", fontsize=9.5, color="#b9770e", rotation=ang2)

# 点
ax.plot(*A, "^", ms=13, mfc="#f1c40f", mec="k", mew=1.0, zorder=6,
        label="已知基准点 A（H=79.568 m）")
ax.plot(*B, "o", ms=11, mfc="#2ecc71", mec="k", mew=1.0, zorder=6,
        label="基准点 B、C")
ax.plot(*C, "o", ms=11, mfc="#2ecc71", mec="k", mew=1.0, zorder=6)
for k, p in P.items():
    ax.plot(*p, "s", ms=9, mfc="#e74c3c", mec="k", mew=0.8, zorder=6,
            label="变形监测点（房角）" if k == "P1" else None)
    ax.annotate(k, p, textcoords="offset points", xytext=(0, 11),
                ha="center", fontsize=10.5, fontweight="bold", color="#922b21")

ax.annotate("A", A, textcoords="offset points", xytext=(-18, 12), fontsize=12,
            fontweight="bold")
ax.annotate("B", B, textcoords="offset points", xytext=(8, 12), fontsize=12,
            fontweight="bold")
ax.annotate("C", C, textcoords="offset points", xytext=(10, 6), fontsize=12,
            fontweight="bold")
ax.annotate("已知点\nH = 79.568 m", A, textcoords="offset points",
            xytext=(-10, -34), ha="center", fontsize=8.5, color="0.25")
ax.annotate("H = 84.018 m", B, textcoords="offset points", xytext=(0, -20),
            ha="center", fontsize=8.5, color="0.25")
ax.annotate("H = 83.806 m", C, textcoords="offset points", xytext=(-4, 14),
            ha="center", fontsize=8.5, color="0.25")

ax.set_title(f"建筑物沉降观测点位布设及观测路线示意图\n"
             f"基准点闭合环 A→B→C→A，环长 {AB+BC+CA:.3f} m；"
             f"变形监测点 P1～P4 位于 A→B 边上", fontsize=12.5)
ax.set_xlabel("X（m）")
ax.set_ylabel("Y（m）")
ax.grid(ls=":", color="0.85")
ax.set_aspect("equal", adjustable="datalim")
ax.set_xlim(-55, max(xc, AB) + 70)
ax.set_ylim(-110, yc + 75)
ax.legend(loc="upper left", fontsize=8.8, framealpha=0.95, ncol=1)

x0, x1 = ax.get_xlim()
y0, y1 = ax.get_ylim()
fr = 50.0 / (x1 - x0)
xs0, ys0 = x0 + 0.05 * (x1 - x0), y0 + 0.05 * (y1 - y0)
ax.plot([xs0, xs0 + fr], [ys0, ys0], "-", color="k", lw=3,
        solid_capstyle="butt")
ax.text(xs0 + fr / 2, ys0 + 4, "50 m", ha="center", fontsize=8.5)
fig.tight_layout()
f = os.path.join(OUT, "观测路线示意图.png")
fig.savefig(f, dpi=220, facecolor="white")
print("saved", f)
