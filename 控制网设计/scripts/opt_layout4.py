# -*- coding: utf-8 -*-
"""QZ2 移到北岸桥头(660) 后, 重新优化其余 6 点位置, 两方案均满足指标"""
import math
import random
import sys

import cnet

sys.stdout.reconfigure(encoding="utf-8")
random.seed(2026)
EDGES0 = cnet.EDGES0
BASE = cnet.build_obs(EDGES0)
AXIS = {"QZ1": (0.0, 0.0), "QZ2": (660.0, 0.0), "QZ3": (800.0, 0.0)}


def set_xy(par):
    x1, x2, xb, yb, xn, yn = par
    cnet.XY.clear()
    cnet.XY.update(AXIS)
    cnet.XY.update({
        "QN1": (x1, 0.0), "QN2": (x2, 0.0),
        "BX": (xb, -yb), "BD": (xb, yb),
        "NN": (xn, -yn), "ND": (xn, yn)})


def evaluate(par):
    x1, x2, xb, yb, xn, yn = par
    if not (x2 < x1 < -80) or yb < 150 or yn < 150 or xb < 820 or xn > -300:
        return None
    set_xy(par)
    for a, b in EDGES0:
        if cnet.dist(a, b) < 200:
            return None
    try:
        r1 = cnet.precision_obs(BASE, cnet.FIX1)
        r2 = cnet.precision_obs(BASE, cnet.FIX2)
    except Exception:
        return None
    m1, m2 = cnet.metrics(r1), cnet.metrics(r2)
    return dict(m1=m1, m2=m2,
                avg=sum(cnet.dist(*e) for e in EDGES0) / len(EDGES0), par=par)


def score(e):
    if e is None:
        return 1e12
    pen = 0.0
    for m in (e["m1"], e["m2"]):
        pen += max(0.0, m["mwp"] - 3.4) * 400
        pen += max(0.0, 145000 - m["rel"]) / 145000 * 900
        pen += max(0.0, m["lo_sig"] - 5.0) * 50
        pen += max(0.0, 330000 - m["lo_rel"]) / 330000 * 50
    pen += abs(e["avg"] - 900) / 900 * 10
    return pen * 10 + max(e["m1"]["mwp"], e["m2"]["mwp"])


best_par = [-346.8, -503.0, 831.6, 294.2, -429.6, 232.8]
best_e = evaluate(best_par)
best = score(best_e)
print(f"初值 方案1 {best_e['m1']['mwp']:.3f} / 方案2 {best_e['m2']['mwp']:.3f} mm")

STEP = [80.0] * 6
for it in range(16000):
    par = list(best_par)
    for i in random.sample(range(6), random.choice([1, 1, 2, 3])):
        par[i] += random.uniform(-STEP[i], STEP[i])
    if it % 3200 == 3199:
        STEP = [x * 0.5 for x in STEP]
    e = evaluate(par)
    sc = score(e)
    if sc < best:
        best, best_e, best_par = sc, e, par

set_xy(best_par)
print("最优布设:")
print(f"  QZ1 (0,0)  QZ2 (660,0)  QZ3 (800,0)")
for k in ["QN1", "QN2", "BX", "BD", "NN", "ND"]:
    print(f"  {k}: ({cnet.XY[k][0]:.1f}, {cnet.XY[k][1]:.1f})")
for nm, m in [("方案1", best_e["m1"]), ("方案2", best_e["m2"])]:
    print(f"{nm} 初始: 最弱点 {m['wp']} {m['mwp']:.3f} | 最弱边 {m['we']} "
          f"1/{m['rel']:,.0f} | 最远 {m['lo_sig']:.3f} 1/{m['lo_rel']:,.0f} "
          f"满足 {cnet.meets(m)}")
L = [cnet.dist(*e) for e in EDGES0]
print(f"边长 {min(L):.0f}~{max(L):.0f} m 平均 {sum(L)/len(L):.0f} m")
print("PARAM:", [round(v, 1) for v in best_par])
