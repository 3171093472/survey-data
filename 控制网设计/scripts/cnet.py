# -*- coding: utf-8 -*-
"""
桥梁 GNSS 施工控制网 模拟优化设计 —— 计算内核
9 点边角网: 方向 1.8″, 边长 2mm + 2ppm
方案1: 固定一点一方向(QZ2 坐标 + QZ2→QZ3 方位角)
方案2: 固定 QZ1、QZ2 两点
"""
import itertools
import math
import sys

import numpy as np

RHO = 206264.806247
SIG_DIR = 1.8
A_D = 2.0
B_D = 2e-6

PTS = ["QZ1", "QZ2", "QZ3", "QN1", "QN2", "BX", "BD", "NN", "ND"]
XY = {
    "QZ1": (0.0, 0.0),
    "QZ2": (660.0, 0.0),
    "QZ3": (800.0, 0.0),
    "QN1": (-330.0, 0.0),
    "QN2": (-515.0, 0.0),
    "BX": (895.0, -470.0),
    "BD": (895.0, 470.0),
    "NN": (-355.0, -385.0),
    "ND": (-355.0, 385.0),
}
ALL_EDGES = [e for e in itertools.combinations(PTS, 2)]
EDGES0 = [e for e in ALL_EDGES if set(e) != {"BD", "NN"}]

IDX = {}
for i, p in enumerate(PTS):
    IDX[("x", p)] = 2 * i
    IDX[("y", p)] = 2 * i + 1
for i, p in enumerate(PTS):
    IDX[("z", p)] = 2 * len(PTS) + i
NU = 3 * len(PTS)


def azim(p, q):
    x1, y1 = XY[p]
    x2, y2 = XY[q]
    return math.atan2(y2 - y1, x2 - x1) % (2 * math.pi)


def dist(p, q):
    x1, y1 = XY[p]
    x2, y2 = XY[q]
    return math.hypot(x2 - x1, y2 - y1)


def build_obs(edges):
    obs = []
    for (p, q) in edges:
        obs.append(("D", p, q))
        obs.append(("F", p, q))
        obs.append(("F", q, p))
    return obs


def fixed_cols_of(fixed):
    fc = set()
    for p in fixed.get("points", []):
        fc |= {IDX[("x", p)], IDX[("y", p)]}
    if "point" in fixed:
        p = fixed["point"]
        fc |= {IDX[("x", p)], IDX[("y", p)]}
    if "azimuth" in fixed:
        p, q = fixed["azimuth"]
        fc.add(IDX[("z", p)])
    return fc


def design_matrix(obs):
    n = len(obs)
    A = np.zeros((n, NU))
    pv = np.zeros(n)
    for k, (typ, p, q) in enumerate(obs):
        if typ == "D":
            S = dist(p, q)
            al = azim(p, q)
            ca, sa = math.cos(al), math.sin(al)
            A[k, IDX[("x", p)]] = -ca
            A[k, IDX[("y", p)]] = -sa
            A[k, IDX[("x", q)]] = ca
            A[k, IDX[("y", q)]] = sa
            pv[k] = 1.0 / (A_D + B_D * S * 1000.0) ** 2
        else:
            S = dist(p, q)
            al = azim(p, q)
            ca, sa = math.cos(al), math.sin(al)
            kk = RHO / (1000.0 * S)
            A[k, IDX[("x", p)]] = kk * sa
            A[k, IDX[("y", p)]] = -kk * ca
            A[k, IDX[("x", q)]] = -kk * sa
            A[k, IDX[("y", q)]] = kk * ca
            A[k, IDX[("z", p)]] = 1.0
            pv[k] = 1.0 / SIG_DIR ** 2
    return A, pv


def precision_obs(obs, fixed):
    A, pv = design_matrix(obs)
    free = [i for i in range(NU) if i not in fixed_cols_of(fixed)]
    Af = A[:, free]
    P = np.diag(pv)
    N = Af.T @ P @ Af
    Q = np.linalg.inv(N)
    n = len(obs)
    t = len(free)
    Qf = np.zeros((NU, NU))
    Qf[np.ix_(free, free)] = Q
    pt = {p: math.sqrt(max(Qf[IDX[("x", p)], IDX[("x", p)]]
                           + Qf[IDX[("y", p)], IDX[("y", p)]], 0.0))
          for p in PTS}
    edges = sorted({(o[1], o[2]) if o[1] < o[2] else (o[2], o[1])
                    for o in obs if o[0] == "D"})
    eg = {}
    for (p, q) in edges:
        S = dist(p, q)
        al = azim(p, q)
        ca, sa = math.cos(al), math.sin(al)
        J = np.zeros(NU)
        J[IDX[("x", p)]] = -ca
        J[IDX[("y", p)]] = -sa
        J[IDX[("x", q)]] = ca
        J[IDX[("y", q)]] = sa
        sg = math.sqrt(max(float(J @ Qf @ J.T), 0.0))
        eg[(p, q)] = (S, sg, S * 1000.0 / sg if sg > 0 else 1e18)
    QAAt = A @ Qf @ A.T
    ri = np.array([(1.0 / pv[k] - QAAt[k, k]) * pv[k] for k in range(n)])
    return dict(Q=Qf, t=t, n=n, rbar=(n - t) / n, pt=pt, eg=eg, ri=ri, obs=obs)


def metrics(r):
    wp = max(r["pt"], key=r["pt"].get)
    we = min(r["eg"], key=lambda e: r["eg"][e][2])
    lo = max(r["eg"], key=lambda e: r["eg"][e][0])
    return dict(wp=wp, mwp=r["pt"][wp], we=we, S=r["eg"][we][0],
                swe=r["eg"][we][1], rel=r["eg"][we][2], lo=lo,
                L=r["eg"][lo][0], lo_sig=r["eg"][lo][1], lo_rel=r["eg"][lo][2])


REQ = dict(mwp=4.0, rel=120000, lo_sig=5.0, lo_rel=300000)


def meets(m):
    return (m["mwp"] <= REQ["mwp"] and m["rel"] >= REQ["rel"]
            and m["lo_sig"] <= REQ["lo_sig"] and m["lo_rel"] >= REQ["lo_rel"])


FIX1 = dict(point="QZ2", azimuth=("QZ2", "QZ3"))
FIX2 = dict(points=["QZ1", "QZ2"])


def n_dirs_per_station(obs):
    c = {p: 0 for p in PTS}
    for o in obs:
        if o[0] == "F":
            c[o[1]] += 1
    return c


def optimize(fixed, target_r, base_obs=None, log=True):
    """按多余观测分量由大到小逐个删减观测, 直到平均多余观测分量达标
       每次删减都保证精度指标仍满足设计要求"""
    obs = list(base_obs if base_obs is not None else build_obs(EDGES0))
    t = len([i for i in range(NU) if i not in fixed_cols_of(fixed)])
    n_target = int(round(t / (1.0 - target_r)))
    removed = []
    while len(obs) > n_target:
        r = precision_obs(obs, fixed)
        order = np.argsort(-r["ri"])
        accepted = False
        for k in order:
            cand_obs = obs[:k] + obs[k + 1:]
            nd = n_dirs_per_station(cand_obs)
            if min(nd.values()) < 2:          # 每站至少保留 2 个方向
                continue
            try:
                rr = precision_obs(cand_obs, fixed)
            except np.linalg.LinAlgError:
                continue
            m = metrics(rr)
            if meets(m):
                removed.append(obs[k])
                obs = cand_obs
                accepted = True
                break
        if not accepted:
            break
    r = precision_obs(obs, fixed)
    if log:
        m = metrics(r)
        nd = sum(1 for o in obs if o[0] == "D")
        nf = len(obs) - nd
        print(f"  优化到 r̄={target_r}: 方向 {nf} + 边长 {nd} = {len(obs)}"
              f"  实际 r̄={r['rbar']:.4f}")
        print(f"    最弱点 {m['wp']} {m['mwp']:.3f} mm | 最弱边 {m['we']} "
              f"{m['S']:.0f}m σ={m['swe']:.3f} 1/{m['rel']:,.0f}")
        print(f"    最远点 {m['lo']} {m['L']:.0f}m {m['lo_sig']:.3f} mm "
              f"1/{m['lo_rel']:,.0f} | 满足要求: {meets(m)}")
    return obs, r, removed


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    L = [dist(*e) for e in EDGES0]
    print(f"初始全边角网 {len(EDGES0)} 条对向边; 边长 {min(L):.0f}~{max(L):.0f} m,"
          f" 平均 {sum(L)/len(L):.0f} m")
    for name, fix in [("方案1 固定一点一方向", FIX1), ("方案2 固定两点", FIX2)]:
        r = precision_obs(build_obs(EDGES0), fix)
        m = metrics(r)
        print(f"\n【{name} 初始方案】 t={r['t']} n={r['n']} r̄={r['rbar']:.4f}")
        print(f"   最弱点 {m['wp']} {m['mwp']:.3f} mm | 最弱边 {m['we']} "
              f"1/{m['rel']:,.0f} | 最远点 {m['lo']} {m['lo_sig']:.3f} mm "
              f"1/{m['lo_rel']:,.0f} | 满足: {meets(m)}")
        optimize(fix, 0.6)
        optimize(fix, 0.55)
