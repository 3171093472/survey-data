# -*- coding: utf-8 -*-
"""个人成果计算: 二班 202305801025  alpha右=22d25m00s"""
import json
import math
import sys
from curve_core import Curve, dms2deg, fmt_dms, fmt_mileage

sys.stdout.reconfigure(encoding="utf-8")

c = Curve(dms2deg(22, 25, 0))
print("=" * 84)
print("个人参数: 2班  学号 202305801025  后两位 25 → alpha右 = 22°25′00″")
print("=" * 84)

print("\n一、缓和曲线常数")
print(f"  β0 = {fmt_dms(c.beta0)} = {c.beta0:.6f}°")
print(f"  δ0 = β0/3 = {fmt_dms(c.delta0)} = {c.delta0:.6f}°")
print(f"  m  = {c.m:.6f} m      p = {c.p:.6f} m")
print(f"  x0 = {c.x0:.6f} m      y0 = {c.y0:.6f} m")
print("\n二、曲线综合要素")
print(f"  T  = {c.T:.6f} m       L = {c.L:.6f} m")
print(f"  E0 = {c.E0:.6f} m       q = {c.q:.6f} m")
print("\n三、方位角")
for nm, v in [("α12 = α_ZH-JD (已知)", c.a12), ("α21 = JD→ZH", c.a21),
              ("α23 = JD→HZ (α_BN)", c.a23), ("α32 = HZ→JD", c.a32),
              ("α_Eh (JD→QZ)", c.a_Eh)]:
    print(f"  {nm:22s} {fmt_dms(v)}  ({v:.8f}°)")

print("\n四、主点里程")
for nm, v in [("JD", c.jd), ("ZH", c.ZH), ("HY", c.HY), ("QZ", c.QZ),
              ("YH", c.YH), ("HZ", c.HZ)]:
    print(f"  {nm:3s} {fmt_mileage(v)}")
print(f"  检核 ZH+2T-q = {fmt_mileage(c.ZH + 2*c.T - c.q)}")
print(f"  检核 QZ+(2T-L)/2 = {fmt_mileage(c.QZ + (2*c.T - c.L)/2)}")

print("\n五、主点坐标")
for nm, X, Y in [("ZH", c.XZH, c.YZH), ("QZ", c.XQZ, c.YQZ), ("HZ", c.XHZ, c.YHZ),
                 ("JD", c.JDX, c.JDY)]:
    print(f"  {nm:3s} X={X:14.3f}  Y={Y:13.3f}")

print("\n六、逐桩切线支距坐标与大地坐标")
plan = c.station_plan()
print(f"  {'序号':>4s} {'桩号':>14s} {'类别':>5s} {'l(m)':>8s} "
      f"{'x(m)':>9s} {'y(m)':>8s} {'X(m)':>13s} {'Y(m)':>13s}")
allpts = []
seq = 0
# 主点也纳入列表
main = [("ZH", c.ZH), ("HY", c.HY), ("QZ", c.QZ), ("YH", c.YH), ("HZ", c.HZ)]
rows = [(seg, s) for seg, s in plan]
for nm, s in main:
    rows.append((nm, s))
rows.sort(key=lambda t: t[1])
for seg, s in rows:
    x, y = c.local_from_ZH_general(s)
    if seg in ("HS1", "ZH", "HY"):
        l = s - c.ZH if seg != "CIR" else 0
    if seg == "HS1":
        l = s - c.ZH
    elif seg == "HS2":
        l = c.HZ - s
    elif seg in ("CIR", "QZ", "YH"):
        l = s - c.HY
    elif seg == "ZH":
        l = 0.0
    elif seg == "HY":
        l = c.ls
    elif seg == "HZ":
        l = 0.0
    if seg == "HS2":
        X, Y = c.to_geo_from_HZ(*c.local_second_spiral(l))
    else:
        X, Y = c.to_geo_from_ZH(x, y)
    seq += 1
    print(f"  {seq:4d} {fmt_mileage(s):>14s} {seg:>5s} {l:8.3f} "
          f"{x:9.3f} {y:8.3f} {X:13.3f} {Y:13.3f}")
    allpts.append(dict(seq=seq, seg=seg, mileage=s, l=l, x=x, y=y, X=X, Y=Y))

print(f"\n  合计 {len(allpts)} 个点位")

print("\n七、放样数据 (偏角法)")
print("  置镜 ZH、后视 JD:")
for p in allpts:
    if p["seg"] in ("ZH",):
        continue
    ang = math.degrees(math.atan2(p["y"], p["x"]))
    ch = math.hypot(p["x"], p["y"])
    print(f"    {fmt_mileage(p['mileage']):>14s}  右转 {fmt_dms(ang)}  弦长 {ch:8.3f}")

print("\n  置镜 HZ、后视 JD (第二缓和曲线):")
for p in allpts:
    if p["seg"] not in ("HS2",) and p["seg"] != "YH":
        continue
    lp = c.HZ - p["mileage"]
    x2, y2 = c.local_second_spiral(lp)
    ang = math.degrees(math.atan2(y2, x2))
    ch = math.hypot(x2, y2)
    print(f"    {fmt_mileage(p['mileage']):>14s}  右转 {fmt_dms(ang)}  弦长 {ch:8.3f}")

json.dump(dict(points=allpts), open("points.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n已保存 points.json")
