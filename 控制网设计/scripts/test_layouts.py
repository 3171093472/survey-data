# -*- coding: utf-8 -*-
"""试验不同点位布设, 使初始全边角网满足设计要求"""
import itertools
import math
import sys

import cnet

sys.stdout.reconfigure(encoding="utf-8")

LAYOUTS = {
    "A 原方案(角点远)": {
        "QZ1": (0, 0), "QZ2": (400, 0), "QZ3": (800, 0),
        "QN1": (-150, 0), "QN2": (-320, 0),
        "BX": (1350, -520), "BD": (1350, 520),
        "NN": (-780, -430), "ND": (-780, 430)},
    "B 角点内收": {
        "QZ1": (0, 0), "QZ2": (400, 0), "QZ3": (800, 0),
        "QN1": (-200, 0), "QN2": (-450, 0),
        "BX": (1000, -350), "BD": (1000, 350),
        "NN": (-620, -350), "ND": (-650, 350)},
    "C 两岸对称": {
        "QZ1": (0, 0), "QZ2": (400, 0), "QZ3": (800, 0),
        "QN1": (-220, 0), "QN2": (-480, 0),
        "BX": (1050, -420), "BD": (1050, 420),
        "NN": (-600, -420), "ND": (-600, 420)},
    "D 加宽横向": {
        "QZ1": (0, 0), "QZ2": (400, 0), "QZ3": (800, 0),
        "QN1": (-200, 0), "QN2": (-420, 0),
        "BX": (1000, -550), "BD": (1000, 550),
        "NN": (-560, -550), "ND": (-560, 550)},
    "E 梯形": {
        "QZ1": (0, 0), "QZ2": (400, 0), "QZ3": (800, 0),
        "QN1": (-250, 0), "QN2": (-520, 0),
        "BX": (1100, -300), "BD": (1100, 300),
        "NN": (-650, -300), "ND": (-650, 300)},
}

for name, xy in LAYOUTS.items():
    cnet.XY.clear()
    cnet.XY.update(xy)
    cnet.EDGES0 = [e for e in cnet.ALL_EDGES if set(e) != {"BD", "NN"}]
    r = cnet.precision(cnet.EDGES0, cnet.FIX1)
    wp = max(r["pt"], key=r["pt"].get)
    we = min(r["eg"], key=lambda e: r["eg"][e][2])
    lo = max(r["eg"], key=lambda e: r["eg"][e][0])
    S, sg, rel = r["eg"][we]
    L, lg, lrel = r["eg"][lo]
    avg = sum(cnet.dist(*e) for e in cnet.EDGES0) / len(cnet.EDGES0)
    ok1 = "OK" if r["pt"][wp] <= 4.0 else "×"
    ok2 = "OK" if rel >= 120000 else "×"
    ok3 = "OK" if (lg <= 5.0 and lrel >= 300000) else "×"
    print(f"{name}: 平均边长={avg:6.0f}m")
    print(f"   最弱点 {wp} {r['pt'][wp]:.3f}mm {ok1} | 最弱边 {we} "
          f"S={S:.0f} σ={sg:.3f} 1/{rel:,.0f} {ok2}")
    print(f"   最远 {lo} S={L:.0f} σ={lg:.3f} 1/{lrel:,.0f} {ok3}")
