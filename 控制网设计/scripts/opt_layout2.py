# -*- coding: utf-8 -*-
"""对称约束下优化点位: QN1/QN2 在桥轴线上, BX/BD、NN/ND 关于轴线对称"""
import math
import random
import sys

import cnet

sys.stdout.reconfigure(encoding="utf-8")
random.seed(7)

EDGES0 = [e for e in cnet.ALL_EDGES if set(e) != {"BD", "NN"}]
cnet.EDGES0 = EDGES0


def make_xy(x1, x2, xb, yb, xn, yn):
    return {
        "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
        "QN1": (x1, 0.0), "QN2": (x2, 0.0),
        "BX": (xb, -yb), "BD": (xb, yb),
        "NN": (xn, -yn), "ND": (xn, yn),
    }


def evaluate(par):
    x1, x2, xb, yb, xn, yn = par
    if not (x2 < x1 < -80):
        return None
    if yb < 150 or yn < 150 or xb < 820 or xn > -350:
        return None
    xy = make_xy(*par)
    cnet.XY.clear()
    cnet.XY.update(xy)
    for a, b in EDGES0:
        if cnet.dist(a, b) < 150:
            return None
    try:
        r = cnet.precision(EDGES0, cnet.FIX1)
    except Exception:
        return None
    wp = max(r["pt"], key=r["pt"].get)
    we = min(r["eg"], key=lambda e: r["eg"][e][2])
    lo = max(r["eg"], key=lambda e: r["eg"][e][0])
    S, sg, rel = r["eg"][we]
    L, lg, lrel = r["eg"][lo]
    return dict(par=par, wp=wp, mwp=r["pt"][wp], we=we, rel=rel, lo=lo, lg=lg,
                lrel=lrel, avg=sum(cnet.dist(*e) for e in EDGES0) / len(EDGES0))


def score(e):
    if e is None:
        return 1e12
    pen = 0.0
    pen += max(0.0, e["mwp"] - 3.6) * 300      # 留 10% 裕量
    pen += max(0.0, 130000 - e["rel"]) / 130000 * 200
    pen += max(0.0, e["lg"] - 5.0) * 50
    pen += max(0.0, 320000 - e["lrel"]) / 320000 * 50
    pen += abs(e["avg"] - 1050) / 1050 * 20     # 平均边长靠近 1.05 km
    return pen * 10 + e["mwp"]


best_par = [-220.0, -480.0, 1050.0, 420.0, -600.0, 420.0]
best_e = evaluate(best_par)
best = score(best_e)
print(f"初值: {best_e['mwp']:.3f} mm, 1/{best_e['rel']:,.0f}, "
      f"{best_e['lg']:.3f} mm, 平均 {best_e['avg']:.0f} m")

STEP = [90, 90, 90, 90, 90, 90]
for it in range(12000):
    par = list(best_par)
    for i in random.sample(range(6), random.choice([1, 1, 2, 3])):
        par[i] += random.uniform(-STEP[i], STEP[i])
    if it % 3000 == 2999:
        STEP = [s * 0.5 for s in STEP]
    e = evaluate(par)
    sc = score(e)
    if sc < best:
        best, best_e, best_par = sc, e, par

x1, x2, xb, yb, xn, yn = best_par
print("\n最优对称布设 (m):")
print(f"  QZ1 (0,0)  QZ2 (400,0)  QZ3 (800,0)   桥长 800 m")
print(f"  QN1 ({x1:.1f}, 0)   QN2 ({x2:.1f}, 0)")
print(f"  BX ({xb:.1f}, {-yb:.1f})   BD ({xb:.1f}, {yb:.1f})")
print(f"  NN ({xn:.1f}, {-yn:.1f})   ND ({xn:.1f}, {yn:.1f})")
print(f"\n最弱点 {best_e['wp']} {best_e['mwp']:.3f} mm")
print(f"最弱边 {best_e['we']} 1/{best_e['rel']:,.0f}")
print(f"最远点 {best_e['lo']} {best_e['lg']:.3f} mm 1/{best_e['lrel']:,.0f}")
L = [cnet.dist(*e) for e in EDGES0]
print(f"边长 {min(L):.0f} ~ {max(L):.0f} m, 平均 {sum(L)/len(L):.0f} m")
print("满足全部设计要求:",
      best_e["mwp"] <= 4.0 and best_e["rel"] >= 120000
      and best_e["lg"] <= 5.0 and best_e["lrel"] >= 300000)
