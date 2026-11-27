# -*- coding: utf-8 -*-
"""生成曲线平面示意图 PNG（真实比例）"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from curve_core import Curve, dms2deg, fmt_dms

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False

c = Curve(dms2deg(22, 25, 0))

mile, s = [], 0.0
while s <= c.L + 1e-9:
    mile.append(c.ZH + s)
    s += 0.5
poly = [c.to_geo_from_ZH(*c.local_from_ZH_general(m)) for m in mile]

main = {"ZH": c.ZH, "HY": c.HY, "QZ": c.QZ, "YH": c.YH, "HZ": c.HZ}
mainxy = {}
for nm, m in main.items():
    if nm == "HY":
        xy = c.to_geo_from_ZH(*c.local_first_spiral(c.ls))
    elif nm == "QZ":
        xy = (c.XQZ, c.YQZ)
    elif nm == "YH":
        xy = c.to_geo_from_ZH(*c.local_circle(c.L - 2 * c.ls))
    else:
        xy = c.to_geo_from_ZH(*c.local_from_ZH_general(m))
    mainxy[nm] = xy

fig, ax = plt.subplots(figsize=(10.0, 7.0))
ax.plot([p[1] for p in poly], [p[0] for p in poly], "-", color="#c0392b", lw=2.8,
        label="曲线（ZH—HY—QZ—YH—HZ）", zorder=3)
ax.plot([c.YZH, c.YJD, c.YHZ], [c.XZH, c.XJD, c.XHZ], "--", color="#2471a3",
        lw=1.3, label="两切线 ZH—JD2—HZ", zorder=2)
for nm, (X, Y) in mainxy.items():
    ax.plot(Y, X, "o", ms=8, mfc="#f5b041", mec="k", mew=0.9, zorder=6,
            label="曲线主点" if nm == "ZH" else None)
ax.plot(c.YJD, c.XJD, "^", ms=9, mfc="#8e44ad", mec="k", mew=0.9, zorder=6,
        label="交点 JD2")

plan = c.station_plan()
pxy = [c.to_geo_from_ZH(*c.local_from_ZH_general(st)) for _, st in plan]
ax.plot([p[1] for p in pxy], [p[0] for p in pxy], ".", ms=5, color="#1b2631",
        zorder=5, label="加桩点（5 m / 10 m / 百米桩）")

lab = {"ZH": (-52, 2), "HY": (-46, 8), "QZ": (-34, 12), "YH": (12, -20),
       "HZ": (-6, -28)}
for nm, (X, Y) in mainxy.items():
    ax.annotate(nm, (Y, X), textcoords="offset points", xytext=lab[nm],
                fontsize=12, fontweight="bold", zorder=7)
ax.annotate("JD2", (c.YJD, c.XJD), textcoords="offset points", xytext=(10, -16),
            fontsize=11.5, fontweight="bold", color="#6c3483", zorder=7)

ax.set_xlabel("Y（m，东）")
ax.set_ylabel("X（m，北）")
ax.set_title("带缓和曲线的圆曲线测设平面示意图（真实比例）", fontsize=13)
ax.grid(ls=":", color="0.75")
ax.ticklabel_format(axis="both", style="plain", useOffset=False)
ax.tick_params(labelsize=9)
ax.set_aspect("equal", adjustable="datalim")

ax.text(0.985, 0.018,
        "R = 200 m，Ls = 30 m，α右 = %s\n"
        "JD2 里程 DK8+667.360   T = %.3f m   L = %.3f m   E = %.3f m" %
        (fmt_dms(c.alpha, 0), c.T, c.L, c.E0),
        transform=ax.transAxes, fontsize=9, va="bottom", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="0.6", alpha=0.95))

ax.legend(loc="upper left", fontsize=8.5, framealpha=0.95)

# 指北针（图幅上方 = X 轴正方向 = 北）
ax.annotate("", xy=(0.46, 0.965), xytext=(0.46, 0.80), xycoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color="k", lw=1.6))
ax.text(0.46, 0.975, "N", transform=ax.transAxes, ha="center", va="bottom",
        fontsize=13, fontweight="bold")

# 比例尺
x0, x1 = ax.get_xlim()
frac20 = 20.0 / (x1 - x0)
xa, ya = 0.055, 0.155
ax.plot([xa, xa + frac20], [ya, ya], "-", color="k", lw=3.5,
        transform=ax.transAxes, solid_capstyle="butt")
ax.text(xa + frac20 / 2, ya + 0.012, "20 m", transform=ax.transAxes,
        ha="center", fontsize=9)

fig.tight_layout()
out = r"C:\Users\31710\OneDrive\Desktop\测量数据\道路曲线测设\曲线平面示意图.png"
fig.savefig(out, dpi=220, facecolor="white")
print("saved", out)
