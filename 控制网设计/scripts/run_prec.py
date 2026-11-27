# -*- coding: utf-8 -*-
"""以"最弱点精度最优"为准则的贪心优化(每次删除使最弱点退化最小的观测)"""
import json
import os
import sys

import numpy as np

import cnet

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (660.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-208.4, 0.0), "QN2": (-339.1, 0.0),
    "BX": (820.0, -188.7), "BD": (820.0, 188.7),
    "NN": (-300.0, -162.2), "ND": (-300.0, 162.2)})
EDGES0 = cnet.EDGES0
BASE = cnet.build_obs(EDGES0)


def n_dirs(obs):
    c = {p: 0 for p in cnet.PTS}
    for o in obs:
        if o[0] == "F":
            c[o[1]] += 1
    return c


def obj(obs, fixed):
    """目标: 最弱点中误差; 次目标: 最弱边相对精度(越小越好取倒数)"""
    r = cnet.precision_obs(obs, fixed)
    m = cnet.metrics(r)
    return m, r


def optimize_precision(fixed, target_r, base_obs, verbose=True):
    obs = list(base_obs)
    t = len([i for i in range(cnet.NU) if i not in cnet.fixed_cols_of(fixed)])
    n_t = int(round(t / (1.0 - target_r)))
    m0, _ = obj(obs, fixed)
    hist = [(len(obs), m0["mwp"], m0["rel"])]
    while len(obs) > n_t:
        best = None
        for k in range(len(obs)):
            cand = obs[:k] + obs[k + 1:]
            if min(n_dirs(cand).values()) < 2:
                continue
            try:
                m, r = obj(cand, fixed)
            except np.linalg.LinAlgError:
                continue
            # 综合: 最弱点为主, 兼顾最弱边相对精度与最远点
            key = (m["mwp"] + max(0.0, 120000 - m["rel"]) / 120000 * 3.0
                   + max(0.0, m["lo_rel"] - 300000) / 300000 * 0.0)
            if best is None or key < best[0]:
                best = (key, k, m, r, cand)
        if best is None:
            break
        khf = best[3]["obs"]
        t = (khf and 0) or 0
        obs = best[4]
        hist.append((len(obs), best[2]["mwp"], best[2]["rel"]))
        if verbose and len(obs) % 10 == 0:
            print(f"    n={len(obs)}  最弱点={best[2]['mwp']:.3f} mm")
    return obs, hist


RES = {}
for name, fix in [("方案1", cnet.FIX1), ("方案2", cnet.FIX2)]:
    print("=" * 60, name)
    for tag, tr in [("一次优化", 0.60), ("二次优化", 0.55)]:
        print(f"  {tag} 目标 r̄={tr}")
        obs, hist = optimize_precision(fix, tr, BASE)
        m, r = obj(obs, fix)
        nd = sum(1 for o in obs if o[0] == "D")
        print(f"    → n={len(obs)} (方向{len(obs)-nd}+边{nd}) r̄={r['rbar']:.4f} "
              f"最弱点 {m['wp']} {m['mwp']:.3f} mm | 最弱边 {m['we']} "
              f"1/{m['rel']:,.0f} | 最远点 {m['lo_sig']:.3f} mm "
              f"1/{m['lo_rel']:,.0f} | 满足 {cnet.meets(m)}")
        RES[f"{name}_{tag}"] = dict(
            n=len(obs), nf=len(obs) - nd, nd=nd, rbar=r["rbar"], mwp=m["mwp"],
            wp=m["wp"], we=list(m["we"]), S=m["S"], swe=m["swe"], rel=m["rel"],
            lo=list(m["lo"]), L=m["L"], lo_sig=m["lo_sig"], lo_rel=m["lo_rel"],
            ok=cnet.meets(m),
            edges=sorted({(min(o[1], o[2]), max(o[1], o[2]))
                          for o in obs if o[0] == "D"}),
            dirs=[(o[1], o[2]) for o in obs if o[0] == "F"])

with open(os.path.join(OUT, "results_prec.json"), "w", encoding="utf-8") as f:
    json.dump({k: {kk: vv for kk, vv in v.items()} for k, v in RES.items()},
              f, ensure_ascii=False, indent=1)
print("\nsaved results_prec.json")
