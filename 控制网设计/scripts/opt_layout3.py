# -*- coding: utf-8 -*-
"""对称约束下优化点位: 同时满足方案1(固定一点一方向)与方案2(固定两点)"""
import math
import random
import sys

import cnet

sys.stdout.reconfigure(encoding="utf-8")
random.seed(11)
EDGES0 = cnet.EDGES0
BASE = cnet.build_obs(EDGES0)


def make_par(x1, x2, xb, yb, xn, yn):
    return (x1, x2, xb, yb, xn, yn)


def set_xy(par):
    x1, x2, xb, yb, xn, yn = par
    cnet.XY.update({
        "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
        "QN1": (x1, 0.0), "QN2": (x2, 0.0),
        "BX": (xb, -yb), "BD": (xb, yb),
        "NN": (xn, -yn), "ND": (xn, yn)})


def evaluate(par):
    x1, x2, xb, yb, xn, yn = par
    if not (x2 < x1 < -80) or yb < 150 or yn < 150 or xb < 820 or xn > -300:
        return None
    set_xy(par)
    for a, b in EDGES0:
        if cnet.dist(a, b) < 150:
            return None
    try:
        r1 = cnet.precision_obs(BASE, cnet.FIX1)
        r2 = cnet.precision_obs(BASE, cnet.FIX2)
    except Exception:
        return None
    m1, m2 = cnet.metrics(r1), cnet.metrics(r2)
    return dict(m1=m1, m2=m2,
                avg=sum(cnet.dist(*e) for e in EDGES0) / len(EDGES0),
                par=par)


def score(e):
    if e is None:
        return 1e12
    m1, m2 = e["m1"], e["m2"]
    pen = 0.0
    for m in (m1, m2):
        pen += max(0.0, m["mwp"] - 3.5) * 400     # 两个方案都留裕量
        pen += max(0.0, 135000 - m["rel"]) / 135000 * 200
        pen += max(0.0, m["lo_sig"] - 5.0) * 50
        pen += max(0.0, 330000 - m["lo_rel"]) / 330000 * 50
    pen += abs(e["avg"] - 1000) / 1000 * 15
    return pen * 10 + max(m1["mwp"], m2["mwp"])


best_par = (-330.0, -515.0, 895.0, 470.0, -355.0, 385.0)
best_e = evaluate(best_par)
best = score(best_e)
print(f"初值: 方案1 {best_e['m1']['mwp']:.3f} / 方案2 {best_e['m2']['mwp']:.3f} mm,"
      f" 平均边长 {best_e['avg']:.0f} m")

STEP = [80.0] * 6
for it in range(15000):
    par = list(best_par)
    for i in random.sample(range(6), random.choice([1, 1, 2, 3])):
        par[i] += random.uniform(-STEP[i], STEP[i])
    if it % 3000 == 2999:
        STEP = [s * 0.5 for s in STEP]
    e = evaluate(par)
    sc = score(e)
    if sc < best:
        best, best_e, best_par = sc, e, par

set_xy(best_par)
for k in ["QN1", "QN2", "BX", "BD", "NN", "ND"]:
    print(f"  {k}: ({cnet.XY[k][0]:.1f}, {cnet.XY[k][1]:.1f})")
for nm, m in [("方案1", best_e["m1"]), ("方案2", best_e["m2"])]:
    print(f"{nm} 初始: 最弱点 {m['wp']} {m['mwp']:.3f} mm | 最弱边 {m['we']} "
          f"1/{m['rel']:,.0f} | 最远点 {m['lo']} {m['lo_sig']:.3f} mm "
          f"1/{m['lo_rel']:,.0f} | 满足 {cnet.meets(m)}")
L = [cnet.dist(*e) for e in EDGES0]
print(f"边长 {min(L):.0f}~{max(L):.0f} m, 平均 {sum(L)/len(L):.0f} m")
print("PARAM:", best_par)
