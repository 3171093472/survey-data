# -*- coding: utf-8 -*-
"""完成 6 种设计方案(初始/一次优化/二次优化 × 两方案)的精度评定"""
import json
import os
import sys

import numpy as np

import cnet

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"

# 最终布设(对称优化结果, 取整到 0.5 m)
cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)})

EDGES0 = cnet.EDGES0
BASE = cnet.build_obs(EDGES0)
L = [cnet.dist(*e) for e in EDGES0]
print(f"初始全边角网: {len(EDGES0)} 条对向边, 边长 {min(L):.0f}~{max(L):.0f} m,"
      f" 平均 {sum(L)/len(L):.0f} m\n")


def n_dirs(obs):
    c = {p: 0 for p in cnet.PTS}
    for o in obs:
        if o[0] == "F":
            c[o[1]] += 1
    return c


def valid(obs):
    return min(n_dirs(obs).values()) >= 2


def forced_optimize(fixed, target_r, base_obs):
    """按多余观测分量从大到小删减, 直到平均多余观测分量达到目标"""
    obs = list(base_obs)
    t = len([i for i in range(cnet.NU) if i not in cnet.fixed_cols_of(fixed)])
    n_t = int(round(t / (1.0 - target_r)))
    guard = 0
    while len(obs) > n_t and guard < 400:
        guard += 1
        r = cnet.precision_obs(obs, fixed)
        order = np.argsort(-r["ri"])
        done = False
        for k in order:
            k = int(k)
            cand = obs[:k] + obs[k + 1:]
            if not valid(cand):
                continue
            try:
                cnet.precision_obs(cand, fixed)
            except np.linalg.LinAlgError:
                continue
            obs = cand
            done = True
            break
        if not done:
            break
    return obs


def summarize(tag, obs, fixed):
    r = cnet.precision_obs(obs, fixed)
    m = cnet.metrics(r)
    nd = sum(1 for o in obs if o[0] == "D")
    nf = len(obs) - nd
    return dict(tag=tag, nf=nf, nd=nd, n=len(obs), t=r["t"],
                rbar=r["rbar"], mwp=m["mwp"], wp=m["wp"], we=m["we"],
                S=m["S"], swe=m["swe"], rel=m["rel"], lo=m["lo"], L=m["L"],
                lo_sig=m["lo_sig"], lo_rel=m["lo_rel"], ok=cnet.meets(m))


RESULTS = []
for name, fix in [("方案1", cnet.FIX1), ("方案2", cnet.FIX2)]:
    print("=" * 70)
    print(f"{name}: 未知数 t={len([i for i in range(cnet.NU) if i not in cnet.fixed_cols_of(fix)])}")
    init = summarize("初始方案", BASE, fix)
    print(f"  初始: 方向{init['nf']}+边{init['nd']}={init['n']} r̄={init['rbar']:.4f}"
          f" | 最弱点 {init['wp']} {init['mwp']:.3f}mm | 最弱边 {init['we']}"
          f" 1/{init['rel']:,.0f} | 最远点 {init['lo']} {init['lo_sig']:.3f}mm"
          f" 1/{init['lo_rel']:,.0f} | 满足:{init['ok']}")
    o6 = forced_optimize(fix, 0.60, BASE)
    s6 = summarize("第一次优化", o6, fix)
    print(f"  一次优化(r̄→0.60): 方向{s6['nf']}+边{s6['nd']}={s6['n']}"
          f" r̄={s6['rbar']:.4f} | 最弱点 {s6['wp']} {s6['mwp']:.3f}mm | "
          f"最弱边 {s6['we']} 1/{s6['rel']:,.0f} | 最远点 {s6['lo']} "
          f"{s6['lo_sig']:.3f}mm 1/{s6['lo_rel']:,.0f} | 满足:{s6['ok']}")
    o55 = forced_optimize(fix, 0.55, o6)
    s55 = summarize("第二次优化", o55, fix)
    print(f"  二次优化(r̄→0.55): 方向{s55['nf']}+边{s55['nd']}={s55['n']}"
          f" r̄={s55['rbar']:.4f} | 最弱点 {s55['wp']} {s55['mwp']:.3f}mm | "
          f"最弱边 {s55['we']} 1/{s55['rel']:,.0f} | 最远点 {s55['lo']} "
          f"{s55['lo_sig']:.3f}mm 1/{s55['lo_rel']:,.0f} | 满足:{s55['ok']}")
    for tag, obs in [("初始方案", BASE), ("第一次优化", o6), ("第二次优化", o55)]:
        e = summarize(tag, obs, fix)
        e["scheme"] = name
        e["edges"] = [[a, b] for (a, b) in
                      sorted({(min(o[1], o[2]), max(o[1], o[2]))
                              for o in obs if o[0] == "D"})]
        e["dirs"] = [[o[1], o[2]] for o in obs if o[0] == "F"]
        RESULTS.append(e)

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
    json.dump(dict(points={k: list(v) for k, v in cnet.XY.items()},
                   results=RESULTS), f, ensure_ascii=False, indent=1)
print("\nsaved results.json;", len(RESULTS), "个方案")
