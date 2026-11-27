# -*- coding: utf-8 -*-
"""生成三维激光扫描综述配图: 原理示意图 + 作业流程图"""
import math
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

sys.stdout.reconfigure(encoding="utf-8")
plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\精密仪器综述"
os.makedirs(OUT, exist_ok=True)

# ---------------- 图1 原理示意图 ----------------
fig, ax = plt.subplots(figsize=(8.0, 5.2))
ax.set_xlim(-1.2, 7.2)
ax.set_ylim(-1.4, 4.6)
ax.set_aspect("equal")
ax.axis("off")

# 坐标系
O = (0.0, 0.0)
ax.annotate("", xy=(2.2, 0), xytext=O,
            arrowprops=dict(arrowstyle="-|>", color="#2471a3", lw=1.6))
ax.annotate("", xy=(0, 2.4), xytext=O,
            arrowprops=dict(arrowstyle="-|>", color="#2471a3", lw=1.6))
ax.annotate("", xy=(-0.9, -0.9), xytext=O,
            arrowprops=dict(arrowstyle="-|>", color="#2471a3", lw=1.2,
                            linestyle=(0, (4, 3))))
ax.text(2.25, -0.18, "X（北）", fontsize=12, color="#2471a3")
ax.text(0.10, 2.42, "Z（天顶）", fontsize=12, color="#2471a3")
ax.text(-1.15, -1.05, "Y（东）", fontsize=9, color="#2471a3")

# 扫描仪
ax.add_patch(plt.Rectangle((-0.28, -0.22), 0.56, 0.44, fc="#f5b041",
                           ec="k", lw=1.0, zorder=5))
ax.plot(0, 0.25, "o", ms=4, color="k", zorder=6)
ax.text(0, -0.52, "地面三维激光扫描仪\n（测站）", ha="center", va="top",
        fontsize=9)

# 目标点 P
P = (5.2, 3.3)
ax.plot(*P, "o", ms=9, mfc="#e74c3c", mec="k", mew=0.8, zorder=6)
ax.text(P[0] + 0.12, P[1] + 0.12, "目标点 P(X, Y, Z)", fontsize=12,
        color="#922b21")

# 斜距
ax.annotate("", xy=P, xytext=(0.15, 0.2),
            arrowprops=dict(arrowstyle="-|>", color="#c0392b", lw=1.8,
                            linestyle="-"))
ax.text(2.85, 1.12, "斜距 S", fontsize=13, color="#c0392b", rotation=32,
        fontweight="bold")

# 角度
arc = plt.matplotlib.patches.Arc(O, 2.4, 2.4, theta1=32.4, theta2=90,
                                 color="#27ae60", lw=1.6)
ax.add_patch(arc)
ax.text(0.25, 1.35, "天顶距 θ", fontsize=12.5, color="#27ae60")
arc2 = plt.matplotlib.patches.Arc(O, 3.2, 3.2, theta1=0, theta2=32.4,
                                  color="#8e44ad", lw=1.6)
ax.add_patch(arc2)
ax.text(1.7, 0.28, "水平角 α", fontsize=12.5, color="#8e44ad")

# 坐标计算框
ax.text(3.9, 0.35,
        "X = S·sin θ·cos α\nY = S·sin θ·sin α\nZ = S·cos θ",
        fontsize=13, bbox=dict(boxstyle="round,pad=0.45", fc="#eaf2f8",
                               ec="#2471a3", lw=1.2))
# 地面
ax.plot([-1.1, 7.0], [-1.15, -1.15], color="0.55", lw=1.2)
ax.text(6.0, -1.32, "地面", fontsize=9, color="0.4")
ax.set_title("地面三维激光扫描测量原理示意图", fontsize=13)
fig.tight_layout()
f1 = os.path.join(OUT, "扫描原理示意图.png")
fig.savefig(f1, dpi=220, facecolor="white")
plt.close(fig)
print("saved", f1)

# ---------------- 图2 作业流程图 ----------------
steps = ["踏勘与\n方案设计", "控制点布设\n与靶标设置", "仪器安置\n与参数设置",
         "分站扫描\n（多视点）", "点云配准\n（拼接）", "去噪、滤波\n与简化",
         "特征提取\n建模/成图", "成果输出\n与精度评定"]
fig, ax = plt.subplots(figsize=(8.4, 2.55))
ax.set_xlim(0, 8)
ax.set_ylim(0, 3)
ax.axis("off")
for i, s in enumerate(steps):
    x = 0.15 + i * 0.97
    ax.add_patch(FancyBboxPatch((x, 0.85), 0.82, 1.05,
                                boxstyle="round,pad=0.04",
                                fc="#d6eaf8" if i % 2 == 0 else "#d5f5e3",
                                ec="#2874a6", lw=1.2))
    ax.text(x + 0.41, 1.38, s, ha="center", va="center", fontsize=11.5)
    if i < len(steps) - 1:
        ax.annotate("", xy=(x + 0.97, 1.38), xytext=(x + 0.82, 1.38),
                    arrowprops=dict(arrowstyle="-|>", color="k", lw=1.3))
ax.set_title("地面三维激光扫描作业流程", fontsize=15)
fig.tight_layout()
f2 = os.path.join(OUT, "作业流程图.png")
fig.savefig(f2, dpi=220, facecolor="white")
plt.close(fig)
print("saved", f2)
