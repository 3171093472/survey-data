# -*- coding: utf-8 -*-
"""独立校核: 用数值积分重算全部坐标, 与已生成 Excel 中的成果逐点比对"""
import math
import sys
import openpyxl

sys.stdout.reconfigure(encoding="utf-8")
D2R = math.pi / 180.0

# --- 独立参数 ---
alpha = 22 + 25 / 60.0
R, ls, JD = 200.0, 30.0, 8667.36
X2, Y2 = 2554946.967, 859650.766
a12 = 203 + 50 / 60.0 + 38.8 / 3600.0

m = ls / 2 - ls ** 3 / (240 * R ** 2)
p = ls ** 2 / (24 * R)
T = m + (R + p) * math.tan(alpha * D2R / 2)
L = 2 * ls + math.pi * R / 180 * (alpha - 2 * math.degrees(ls / (2 * R)))
beta0 = math.degrees(ls / (2 * R))
ZH, HY, HZ = JD - T, JD - T + ls, JD - T + L
XZH = X2 + T * math.cos((a12 + 180) * D2R)
YZH = Y2 + T * math.sin((a12 + 180) * D2R)

print(f"独立算: T={T:.6f} L={L:.6f} beta0={beta0:.6f}")
print(f"        ZH={ZH:.6f} HY={HY:.6f} HZ={HZ:.6f}")
print(f"        X_ZH={XZH:.3f} Y_ZH={YZH:.3f}")


def heading(s):
    """曲线前进方向相对 ZH 切线的转角(弧度, 右转为正)"""
    if s <= ls:
        return s * s / (2 * R * ls)
    if s <= L - ls:
        return beta0 * D2R + (s - ls) / R
    u = L - s
    return alpha * D2R - u * u / (2 * R * ls)


def pos(s):
    n = max(2, 2 * int(abs(s) / 0.01))   # 步数取偶数, 保证复合 Simpson 正确
    X = Y = 0.0
    for i in range(n + 1):
        ss = s * i / n
        th = heading(ss) + a12 * D2R
        w = 1 if i in (0, n) else (4 if i % 2 else 2)
        X += w * math.cos(th)
        Y += w * math.sin(th)
    h = s / n
    return XZH + X * h / 3.0, YZH + Y * h / 3.0


# --- 读 Excel 成果 ---
wb = openpyxl.load_workbook(
    r"C:\Users\31710\OneDrive\Desktop\测量数据\道路曲线测设\道路曲线测设计算成果.xlsx")
ws = wb["8-逐桩大地坐标"]
rows = []
for r in range(1, ws.max_row + 1):
    v = ws.cell(row=r, column=2).value
    if isinstance(v, str) and v.startswith("DK8+"):
        rows.append((ws.cell(row=r, column=2).value,
                     ws.cell(row=r, column=4).value,
                     ws.cell(row=r, column=5).value))

print(f"\nExcel 中点位 {len(rows)} 个; 开始逐点独立校核:")
maxd = 0.0
for mile_txt, Xe, Ye in rows:
    km, rest = mile_txt.split("+")
    st = int(km.replace("DK", "")) * 1000 + float(rest)
    Xi, Yi = pos(st - ZH)
    d = math.hypot(Xi - Xe, Yi - Ye)
    maxd = max(maxd, d)
    flag = "OK " if d < 0.0015 else "!! "
    print(f"  {flag}{mile_txt:>14s}  Excel({Xe:14.3f},{Ye:13.3f})  "
          f"独立({Xi:14.3f},{Yi:13.3f})  差 {d*1000:6.2f} mm")
print(f"\n最大较差 = {maxd*1000:.2f} mm")
print("结论:", "全部点位一致（较差均在桩号取位 0.5mm 量级内）" if maxd < 0.0015 else "存在超限差异，需检查")
