# -*- coding: utf-8 -*-
"""随机搜索优化点位布设, 使初始全边角网满足: 最弱点≤4.0mm、
最弱边相对精度≥1/12万、最远点边中误差≤5.0mm 且≥1/30万"""
import math
import random
import sys

import cnet

sys.stdout.reconfigure(encoding="utf-8")
random.seed(20261124)

AXIS = {"QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0)}
EDGES0 = [e for e in cnet.ALL_EDGES if set(e) != {"BD", "NN"}]
cnet.EDGES0 = EDGES0


def evaluate(xy):
    cnet.XY.clear()
    cnet.XY.update(xy)
    # 保证凸性/不退化
    for a, b in EDGES0:
        if cnet.dist(a, b) < 120:
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
    return dict(r=r, wp=wp, mwp=r["pt"][wp], we=we, rel=rel, lo=lo, lg=lg,
                lrel=lrel, avg=sum(cnet.dist(*e) for e in EDGES0) / len(EDGES0))


def score(e):
    """综合目标: 满足全部约束前提下使最弱点最小"""
    if e is None:
        return 1e9
    pen = 0.0
    pen += max(0.0, e["mwp"] - 4.0) * 100
    pen += max(0.0, 120000 - e["rel"]) / 120000 * 50
    pen += max(0.0, e["lg"] - 5.0) * 20
    pen += max(0.0, 300000 - e["lrel"]) / 300000 * 20
    # 平均边长落在 0.9~1.3 km 更好(符合"基线平均1-2km")
    avg_pen = max(0.0, 900 - e["avg"]) / 900 + max(0.0, e["avg"] - 1300) / 1300
    return pen * 100 + e["mwp"] + avg_pen * 3


best = None
best_e = None
# 初值: C 方案
cur = dict(AXIS)
cur.update({"QN1": (-220, 0), "QN2": (-480, 0),
            "BX": (1050, -420), "BD": (1050, 420),
            "NN": (-600, -420), "ND": (-600, 420)})
e = evaluate(cur)
best_e, best = e, score(e)
print(f"初值: 最弱点 {e['wp']} {e['mwp']:.3f} mm, 最弱边 1/{e['rel']:,.0f}, "
      f"最远 {e['lg']:.3f} mm 1/{e['lrel']:,.0f}, 平均边长 {e['avg']:.0f} m")

STEP = 120.0
for it in range(6000):
    cand = {k: v for k, v in best_xy.items()} if (best_xy := cur) else {}
    # 随机扰动一个或多个点(不含轴线点)
    keys = ["QN1", "QN2", "BX", "BD", "NN", "ND"]
    for k in random.sample(keys, random.choice([1, 1, 2])):
        x, y = cand[k]
        cand[k] = (x + random.uniform(-STEP, STEP),
                   y + random.uniform(-STEP, STEP))
    if it % 1500 == 1499:
        STEP *= 0.55
    ee = evaluate(cand)
    sc = score(ee)
    if sc < best:
        best, best_e, cur = sc, ee, cand
        e = ee

print("\n最优布设:")
for k in ["QN1", "QN2", "BX", "BD", "NN", "ND"]:
    print(f"  {k}: {cur[k]}")
print(f"\n最弱点 {best_e['wp']} {best_e['mwp']:.3f} mm")
print(f"最弱边 {best_e['we']} 1/{best_e['rel']:,.0f}")
print(f"最远点 {best_e['lo']} {best_e['lg']:.3f} mm 1/{best_e['lrel']:,.0f}")
print(f"平均边长 {best_e['avg']:.0f} m")
ok = (best_e["mwp"] <= 4.0 and best_e["rel"] >= 120000 and best_e["lg"] <= 5.0
      and best_e["lrel"] >= 300000)
print("满足全部设计要求:", ok)
