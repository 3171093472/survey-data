# -*- coding: utf-8 -*-
"""用指导书实例(alpha右=26d02m00s)逐点验算公式与桩号编排"""
import math
import sys
from curve_core import Curve, dms2deg, deg2dms, fmt_dms, fmt_mileage

sys.stdout.reconfigure(encoding="utf-8")

c = Curve(dms2deg(26, 2, 0))

print("=" * 78)
print("一、缓和曲线常数与曲线要素")
print("=" * 78)
rows = [
    ("beta0", c.beta0, "4d17m50s"),
    ("delta0", c.delta0, "-"),
    ("m", c.m, "14.997"),
    ("p", c.p, "0.188"),
    ("T", c.T, "61.275"),
    ("L", c.L, "120.873"),
    ("E0", c.E0, "5.467"),
    ("q", c.q, "1.677"),
    ("x0", c.x0, "29.983"),
    ("y0", c.y0, "0.750"),
]
for name, v, ref in rows:
    if name in ("beta0", "delta0"):
        print(f"  {name:8s} {fmt_dms(v)}   手册: {ref}")
    else:
        print(f"  {name:8s} {v:12.6f}  手册: {ref:>10s}   差 {v - float(ref):+.6f}"
              if ref not in ("-",) else f"  {name:8s} {v:12.6f}")

print(f"\n  主点里程: ZH={fmt_mileage(c.ZH)} HY={fmt_mileage(c.HY)} "
      f"QZ={fmt_mileage(c.QZ)} YH={fmt_mileage(c.YH)} HZ={fmt_mileage(c.HZ)}")
print(f"  手册:     ZH=DK8+606.085 HY=DK8+636.085 QZ=DK8+666.522 "
      f"YH=DK8+696.958 HZ=DK8+726.958")
print(f"  检核 ZH+2T-q = {fmt_mileage(c.ZH + 2*c.T - c.q)}  (应等于 HZ)")
print(f"  检核 QZ+(2T-L)/2 = {fmt_mileage(c.QZ + (2*c.T-c.L)/2)}  (应等于 JD)")

print("\n" + "=" * 78)
print("二、主点切线支距坐标 (ZH 切线系)")
print("=" * 78)
mp = [("ZH", c.ZH, 0.0, 0.0), ("HY", c.HY, 29.983, 0.750),
      ("QZ", c.QZ, 60.044, 5.327), ("YH", c.YH, 89.063, 14.407),
      ("HZ", c.HZ, 116.334, 26.893), ("JD", c.jd, 61.275, 0.000)]
for nm, mile, rx, ry in mp:
    if nm == "JD":
        x, y = c.T, 0.0
    elif nm == "ZH":
        x, y = 0.0, 0.0
    elif nm == "HY":
        x, y = c.local_first_spiral(c.ls)
    elif nm == "HZ":
        x, y = c.T + c.T * math.cos(c.alpha * math.pi / 180), c.T * math.sin(c.alpha * math.pi / 180)
    elif nm == "QZ":
        x, y = c.local_circle(c.QZ - c.HY)
    else:
        x, y = c.local_circle(c.YH - c.HY)
    print(f"  {nm:3s} {fmt_mileage(mile)}  X={x:9.3f}(手册{rx:8.3f},差{x-rx:+.3f})"
          f"  Y={y:8.3f}(手册{ry:8.3f},差{y-ry:+.3f})")

print("\n" + "=" * 78)
print("三、加密点（桩号编排沿用实例: ZH起5m网格 + 百米桩, 圆曲线10m）")
print("=" * 78)
ref = [
    (2, 8611.085, 5.000, 0.003), (3, 8616.085, 10.000, 0.028),
    (4, 8621.085, 14.999, 0.094), (5, 8626.085, 19.998, 0.222),
    (6, 8631.085, 24.993, 0.434), (7, 8636.085, 29.983, 0.750),
    (8, 8646.085, 39.932, 1.748), (9, 8656.085, 49.819, 3.242),
    (10, 8666.085, 59.618, 5.229), (11, 8676.085, 69.306, 7.703),
    (12, 8686.085, 78.859, 10.658), (13, 8696.085, 88.252, 14.086),
    (14, 8700.000, 91.881, 15.555), (15, 8701.085, 92.882, 15.973),
    (16, 8706.085, 97.470, 17.960), (17, 8711.085, 102.023, 20.027),
    (18, 8716.085, 106.549, 22.153), (19, 8721.085, 111.054, 24.320),
    (20, 8726.085, 115.550, 26.510),
]
plan = [(seg, s) for seg, s in c.station_plan()]
print(f"  我的编排共 {len(plan)} 个加密点:")
for seg, s in plan:
    print(f"    {seg:3s} {fmt_mileage(s)}")
print(f"  手册共 {len(ref)} 个加密点 (2..20)")

# 逐个比对: 用同桩号序列重算
print("\n  逐点比对 (手册值 vs 本算值):")
print("  编号  桩号            x(手册)   x(本算)   差      y(手册)   y(本算)   差")
sta_ref = {r[1]: r for r in ref}
plan_stations = [s for _, s in plan]
n = 1
maxdx = maxdy = 0.0
for st in plan_stations:
    x, y = c.local_from_ZH_general(st)
    # 找最接近的手册桩号
    key = min(sta_ref, key=lambda k: abs(k - st))
    r = sta_ref[key]
    dx, dy = x - r[2], y - r[3]
    maxdx = max(maxdx, abs(dx)); maxdy = max(maxdy, abs(dy))
    print(f"  {n:3d}  {fmt_mileage(st)}  {r[2]:8.3f} {x:8.3f} {dx:+7.3f}"
          f"  {r[3]:7.3f} {y:7.3f} {dy:+7.3f}")
    n += 1
print(f"\n  最大偏差: dx={maxdx:.3f} m, dy={maxdy:.3f} m")

print("\n" + "=" * 78)
print("四、独立校核")
print("=" * 78)
# 1) QZ 两种算法
xq, yq = c.local_circle(c.QZ - c.HY)
XQ1, YQ1 = c.to_geo_from_ZH(xq, yq)
print(f"  QZ 由圆曲线公式反算: ({XQ1:.3f}, {YQ1:.3f})")
print(f"  QZ 由 E0 与 a_Eh 计算 : ({c.XQZ:.3f}, {c.YQZ:.3f})   差 "
      f"{XQ1-c.XQZ:+.4f}, {YQ1-c.YQZ:+.4f}")
# 2) HZ 两种算法
xhz, yhz = c.T + c.T*math.cos(c.alpha*math.pi/180), c.T*math.sin(c.alpha*math.pi/180)
XH1, YH1 = c.to_geo_from_ZH(xhz, yhz)
print(f"  HZ 由切线支距 → 大地 : ({XH1:.3f}, {YH1:.3f})")
print(f"  HZ 由 a23 直接计算   : ({c.XHZ:.3f}, {c.YHZ:.3f})   差 "
      f"{XH1-c.XHZ:+.4f}, {YH1-c.YHZ:+.4f}")
# 3) 第二缓和曲线: 手册 p22 公式 vs 积分
for lp in (5.0, 15.0, 26.958):
    x2, y2 = c.local_second_spiral(lp)
    Xa, Ya = c.to_geo_from_HZ(x2, y2)      # 手册公式
    xi, yi = c.local_from_HZ_backward(lp)  # 积分
    Xb, Yb = c.to_geo_from_ZH(xi, yi)
    print(f"  lp={lp:6.3f}  手册公式({Xa:12.3f},{Ya:11.3f})  "
          f"积分({Xb:12.3f},{Yb:11.3f})  差 {Xa-Xb:+.4f},{Ya-Yb:+.4f}")
# 4) 弧长校核: 相邻点弦长之和 vs 曲线长
tot = 0.0
prev = None
for seg, s in plan:
    x, y = c.local_from_ZH_general(s)
    if prev is not None:
        tot += math.hypot(x - prev[0], y - prev[1])
    prev = (x, y)
chord_all = math.hypot(prev[0]-0.0, prev[1]-0.0)
print(f"\n  各桩点弦长总和 = {tot:.3f} m ; 曲线长 L = {c.L:.3f} m ; "
      f"ZH→末点弦长 = {chord_all:.3f} m")
