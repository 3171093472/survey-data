# -*- coding: utf-8 -*-
"""生成控制网优化设计 交付物: 手册原表填写版 PDF + Excel 成果"""
import json
import math
import os
import sys

import pymupdf
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cnet   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计"
HB = r"C:\Users\31710\OneDrive\Desktop\测量数据\要求\工程测量实习计划及指导书-叶险峰2026.pdf"
FONT = r"C:\Windows\Fonts\simsun.ttc"
INK = (0.03, 0.10, 0.45)
BLACK = (0, 0, 0)
FT = pymupdf.Font(fontfile=FONT)

cnet.XY.update({
    "QZ1": (0.0, 0.0), "QZ2": (660.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-208.4, 0.0), "QN2": (-339.1, 0.0),
    "BX": (820.0, -188.7), "BD": (820.0, 188.7),
    "NN": (-300.0, -162.2), "ND": (-300.0, 162.2)})
BASE = cnet.build_obs(cnet.EDGES0)

with open(os.path.join(OUT, "results_prec.json"), encoding="utf-8") as f:
    RP = json.load(f)


def eval_obs(obs, fix):
    r = cnet.precision_obs(obs, fix)
    m = cnet.metrics(r)
    nd = sum(1 for o in obs if o[0] == "D")
    return dict(n=len(obs), nf=len(obs) - nd, nd=nd, rbar=r["rbar"],
                mwp=m["mwp"], wp=m["wp"], we=m["we"], S=m["S"], swe=m["swe"],
                rel=m["rel"], lo=m["lo"], L=m["L"], lo_sig=m["lo_sig"],
                lo_rel=m["lo_rel"], t=r["t"])


def obs_from_json(key):
    d = RP[key]
    edges = [tuple(e) for e in d["edges"]]
    dirs = [tuple(x) for x in d["dirs"]]
    obs = [("D", *e) for e in edges] + [("F", *x) for x in dirs]
    return obs


SCHEMES = {}
SCHEMES[("初始方案", "固定两点")] = eval_obs(BASE, cnet.FIX2)
SCHEMES[("初始方案", "固定一点一方向")] = eval_obs(BASE, cnet.FIX1)
SCHEMES[("第一次优化", "固定两点")] = eval_obs(obs_from_json("方案2_一次优化"), cnet.FIX2)
SCHEMES[("第一次优化", "固定一点一方向")] = eval_obs(obs_from_json("方案1_一次优化"), cnet.FIX1)
SCHEMES[("第二次优化", "固定两点")] = eval_obs(obs_from_json("方案2_二次优化"), cnet.FIX2)
SCHEMES[("第二次优化", "固定一点一方向")] = eval_obs(obs_from_json("方案1_二次优化"), cnet.FIX1)

ORDER = [("初始方案", "固定两点"), ("初始方案", "固定一点一方向"),
         ("第一次优化", "固定两点"), ("第一次优化", "固定一点一方向"),
         ("第二次优化", "固定两点"), ("第二次优化", "固定一点一方向")]

print("六种设计方案:")
for k in ORDER:
    s = SCHEMES[k]
    print(f"  {k[0]:6s}{k[1]:8s} n={s['n']:3d}({s['nf']:2d}+{s['nd']:2d}) "
          f"r̄={s['rbar']:.4f} 最弱点 {s['wp']} {s['mwp']:.3f} | 最弱边 "
          f"{s['we'][0]}–{s['we'][1]} {s['S']:.1f}m {s['swe']:.3f}mm "
          f"1/{s['rel']:,.0f} | 最远 {s['lo'][0]}–{s['lo'][1]} {s['L']:.1f}m "
          f"{s['lo_sig']:.3f}mm 1/{s['lo_rel']:,.0f}")

# ---------------- PDF ----------------
src = pymupdf.open(HB)
out = pymupdf.open()


def new_page(w=595.3, h=841.9):
    p = out.new_page(width=w, height=h)
    p.insert_font(fontname="song", fontfile=FONT)
    return p


def hb(pno):
    out.insert_pdf(src, from_page=pno, to_page=pno)
    p = out[-1]
    p.insert_font(fontname="song", fontfile=FONT)
    return p


def put(p, x, y, t, size=9, align="left", color=INK):
    w = FT.text_length(t, fontsize=size)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    p.insert_text((x, y), t, fontname="song", fontsize=size, color=color)


def cellc(p, x0, x1, yc, t, size=8, color=INK, dy=3.0):
    s = size
    while s > 5.5 and FT.text_length(t, fontsize=s) > (x1 - x0) - 2.5:
        s -= 0.2
    put(p, (x0 + x1) / 2, yc + dy, t, size=s, align="center", color=color)


# ---------- 封面 ----------
p = new_page()
p.draw_rect(pymupdf.Rect(56, 60, 539, 285), color=BLACK, width=1.2)
put(p, 297.6, 120, "《 工 程 测 量 实 习 》", 21, "center", BLACK)
put(p, 297.6, 162, "控制网模拟优化设计（必做）", 16.5, "center", BLACK)
put(p, 297.6, 200, "桥 梁 GNSS 施 工 控 制 网", 14, "center", BLACK)
put(p, 297.6, 240, "（按指导书第 28～29 页原表填写）", 10.5, "center", BLACK)
put(p, 297.6, 266, "二〇二六年十一月", 10.5, "center", BLACK)
rows = [("学　　院", "土木工程学院"), ("专　　业", "测绘工程"),
        ("班　　级", "2 班"), ("学　　号", "202305801025"),
        ("姓　　名", ""), ("组　　号", ""), ("指导教师", "叶险峰")]
y0 = 306
p.draw_rect(pymupdf.Rect(140, y0, 460, y0 + 23 * len(rows)), color=BLACK, width=0.8)
for i, (k, v) in enumerate(rows):
    yy = y0 + 23 * i
    if i:
        p.draw_line((140, yy), (460, yy), color=BLACK, width=0.8)
    p.draw_line((215, yy), (215, yy + 23), color=BLACK, width=0.8)
    put(p, 177, yy + 15, k, 10, "center", BLACK)
    put(p, 225, yy + 15, v, 10, "left", BLACK)

y = 500
put(p, 84, y, "一、设计概况", 11.5, "left", BLACK)
y += 19
L = [cnet.dist(*e) for e in cnet.EDGES0]
for t in [
    "桥长 800 m（属大桥），按《公路勘测规范》GNSS 施工控制网等级取三等；"
    "独立平面坐标系。",
    "桥位：在湘江湘潭段卫星影像（中心约 112.9655°E、27.9169°N）上选线，"
    "河宽约 715 m；",
    "800 m 桥跨两岸各约 40 m 引桥，QZ1、QZ3 位于两岸，QZ2 位于河中。",
    f"全网 9 点：桥轴线 QZ1、QZ2、QZ3；南引桥 QN1、QN2；北岸 BX、BD；南岸 NN、ND。",
    f"初始方案为全边角网：35 条对向边、70 个方向值、35 条边长；"
    f"边长 {min(L):.0f}～{max(L):.0f} m，平均 {sum(L)/len(L):.0f} m。",
    "观测精度：方向 1.8″，边长 2 mm + 2 ppm。",
    "方案 1：固定任意一点一方向（QZ2 坐标 + QZ2→QZ3 方位角）；"
    "方案 2：固定 QZ1、QZ2 两点。",
    "设计要求：最弱点精度 ≤4.0 mm；最弱边相对精度优于 1/12 万；"
    "最远点边长中误差 ≤5.0 mm、相对精度优于 1/30 万。",
    "优化方法：解析法——平均多余观测分量 r = 1 - t/n 由 0.77 降至 0.60、0.55，",
    "以“最弱点精度退化最小”为准则逐个删减观测。",
]:
    put(p, 84, y, t, 9.5, "left", BLACK)
    y += 17
y += 6
put(p, 84, y, "二、主要结论", 11.5, "left", BLACK)
y += 19
for t in [
    "初始方案：最弱点 3.500 mm、最弱边 1/13.5 万、最远点 1.63 mm（1/84 万），"
    "三项指标全部满足且裕量较大；",
    "第一次优化（r̄≈0.60）：观测数 105→60（方案1）/58（方案2），"
    "最弱点 3.65/3.78 mm，仍满足全部指标；",
    "第二次优化（r̄≈0.55）：观测数 105→53/51，最弱点 3.76/3.95 mm，"
    "仍满足全部指标；",
    "结论：固定两点方案观测量更少（51 vs 53）而精度相当，推荐采用方案 2 的二次优化布网。",
]:
    put(p, 84, y, t, 9.5, "left", BLACK)
    y += 17

# ---------- 手册 p28: 对比表 (横向) ----------
p = hb(28)
COL = [(59.80, 131.35), (131.35, 194.10), (194.10, 254.85), (254.85, 307.35),
       (307.35, 362.10), (362.10, 405.60), (405.60, 465.60), (465.60, 526.35),
       (526.35, 575.10), (575.10, 651.60), (651.60, 703.35), (703.35, 775.30)]
ROWS = [264.64, 307.64, 350.64, 393.64, 436.64, 479.64]
for (grp, fix), yc in zip(ORDER, ROWS):
    s = SCHEMES[(grp, fix)]
    cellc(p, *COL[2], yc, f"{s['rbar']:.2f}", 8.5)
    cellc(p, *COL[3], yc, str(s["nf"]), 8.5)
    cellc(p, *COL[4], yc, str(s["nd"]), 8.5)
    cellc(p, *COL[5], yc, s["wp"], 8.5)
    cellc(p, *COL[6], yc, f"{s['mwp']:.2f}", 8.5)
    cellc(p, *COL[7], yc, f"{s['we'][0]}–{s['we'][1]}", 8)
    put(p, (COL[8][0] + COL[8][1]) / 2, yc - 2, f"{s['S']:.0f}", 7.5,
        "center")
    put(p, (COL[8][0] + COL[8][1]) / 2, yc + 10, f"{s['swe']:.2f}", 7.5,
        "center")
    cellc(p, *COL[9], yc, f"1/{s['rel']/10000:.1f}万", 8)
    put(p, (COL[10][0] + COL[10][1]) / 2, yc - 2, f"{s['L']:.0f}", 7.5,
        "center")
    put(p, (COL[10][0] + COL[10][1]) / 2, yc + 10, f"{s['lo_sig']:.2f}", 7.5,
        "center")
    cellc(p, *COL[11], yc, f"1/{s['lo_rel']/10000:.0f}万", 8)
pass  # 方案与固定方式已由原表印好

# ---------- 手册 p29: 控制网图 + 分析评价 ----------
p = hb(29)
fig = os.path.join(OUT, "控制网图（影像底图）.png")
if os.path.exists(fig):
    _h = 165.0
    _w = _h * 775.0 / 430.0
    _x0 = (595.3 - _w) / 2
    p.insert_image(pymupdf.Rect(_x0, 119, _x0 + _w, 119 + _h), filename=fig)

yy = 322
put(p, 85, yy, "1. 网形与等级", 10.5, "left", BLACK)
yy += 15
txt1 = [
    "本网在湘江湘潭段卫星影像上选线布设：桥轴线横跨湘江（河宽约 715 m），"
    "QZ1、QZ3 分设两岸，QZ2 位于河中，",
    "桥长 800 m，按大桥三等布设。9 点中 QZ1—QZ2—QZ3",
    "在桥轴线上，QN1、QN2 位于南端引桥，BX、BD 与 NN、ND 分列南北两岸，"
    "点间基线 156～1367 m，",
    "平均 754 m，南北基本对称，图形结构均匀，便于以边角测量方式一次布设、多次使用。",
]
for t in txt1:
    put(p, 85, yy, t, 9, "left", BLACK)
    yy += 14
yy += 4
put(p, 85, yy, "2. 初始方案精度与可靠性", 10.5, "left", BLACK)
yy += 15
s1, s2 = SCHEMES[("初始方案", "固定一点一方向")], SCHEMES[("初始方案", "固定两点")]
for t in [
    f"全边角网共 105 个观测（方向 70、边长 35），平均多余观测分量 "
    f"r = {s1['rbar']:.2f}（固定一点一方向）/ {s2['rbar']:.2f}（固定两点），",
    f"最弱点 {s1['wp']} {s1['mwp']:.2f} mm，最弱边 {s1['we'][0]}–{s1['we'][1]} "
    f"1/{s1['rel']/1e4:.1f} 万，最远点 {s1['lo'][0]}–{s1['lo'][1]} "
    f"{s1['lo_sig']:.2f} mm（1/{s1['lo_rel']/1e4:.0f} 万），三项指标满足且有一定裕量。",
]:
    put(p, 85, yy, t, 9, "left", BLACK)
    yy += 14
yy += 4
put(p, 85, yy, "3. 两次优化设计与结果分析", 10.5, "left", BLACK)
yy += 15
o1a = SCHEMES[("第一次优化", "固定一点一方向")]
o1b = SCHEMES[("第一次优化", "固定两点")]
o2a = SCHEMES[("第二次优化", "固定一点一方向")]
o2b = SCHEMES[("第二次优化", "固定两点")]
for t in [
    f"以“删除后最弱点精度退化最小”为准则逐个删减观测。第一次优化后观测数降至 "
    f"{o1a['n']}（方案1）/{o1b['n']}（方案2），",
    f"第二次优化降至 {o2a['n']}/{o2b['n']}，即观测量减少约 "
    f"{(1-o2b['n']/105)*100:.0f}%，平均多余观测分量由 0.77 降至 0.55。",
    f"精度随观测数减少而缓慢降低：最弱点由 3.50 mm 增至 {o2a['mwp']:.2f} mm（方案1）、"
    f"{o2b['mwp']:.2f} mm（方案2），",
    f"最弱边相对精度 {o1a['rel']/1e4:.1f} 万～{o2b['rel']/1e4:.1f} 万，"
    f"最远点边长中误差 {o1a['lo_sig']:.2f}～{o2b['lo_sig']:.2f} mm，"
    "六种方案全部满足设计指标。",
]:
    put(p, 85, yy, t, 9, "left", BLACK)
    yy += 14
yy += 4
put(p, 85, yy, "4. 两种固定方案对比", 10.5, "left", BLACK)
yy += 15
for t in [
    "固定两点（方案2）以 QZ1、QZ2 为起算基准，网形定向与尺度约束更强；"
    "固定一点一方向（方案1）只固定",
    f"QZ2 及 QZ2→QZ3 方位角。相同观测数下两者精度相当；达到相同 r̄ 时，"
    f"方案2 所需观测数更少",
    f"（{o2b['n']} vs {o2a['n']}），说明固定两点的基准更“省”观测，"
    "工程上宜优先采用方案 2。",
]:
    put(p, 85, yy, t, 9, "left", BLACK)
    yy += 14
yy += 4
put(p, 85, yy, "5. 结论与建议", 10.5, "left", BLACK)
yy += 15
for t in [
    f"① 推荐方案 2（固定 QZ1、QZ2）二次优化后的布网：51 个观测，最弱点 "
    f"{o2b['mwp']:.2f} mm、",
    f"   最弱边 1/{o2b['rel']/1e4:.1f} 万、最远点 {o2b['lo_sig']:.2f} mm，"
    "观测量最省且仍满足全部指标；",
    "② 若顾及施工期点位可能破坏、需保留一定可靠性储备，可采用第一次优化方案"
    "（58 个观测，r̄=0.60）；",
    "③ 初始全边角网虽然精度最好，但观测量偏多（105 个），存在较大冗余，"
    "优化可节省外业工作量约 50%。",
]:
    put(p, 85, yy, t, 9, "left", BLACK)
    yy += 14

# ---------- 附图页(纵向): 三种方案影像底图对照 ----------
p2 = new_page()
put(p2, 297.6, 52, "附图　控制网图（影像底图·三种方案对照）", 13.5, "center", BLACK)
f3 = os.path.join(OUT, "控制网图（影像底图·三联）.png")
if os.path.exists(f3):
    _w = 468.0
    _h = _w * 9.6 / 7.6
    p2.insert_image(pymupdf.Rect(63, 66, 63 + _w, 66 + _h), filename=f3)
    put(p2, 63, 66 + _h + 12,
        "影像底图：Esri World Imagery（湘江 湘潭段，中心约 112.9655°E、"
        "27.9169°N）；黄色线为观测边，红色虚线箭头为仅方向观测。", 8, "left",
        BLACK)

# ---------- 附页 1: 坐标与精度评定明细 ----------
p = new_page()
put(p, 297.6, 70, "附表 1　控制点坐标与各方案精度评定明细", 14, "center", BLACK)
yy = 95
put(p, 84, yy, "一、控制点坐标（独立坐标系，m）", 10.5, "left", BLACK)
yy += 8
cw = [52, 74, 74, 52, 74, 74]
xx = 84
p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cw), yy + 20), color=BLACK, width=0.8)
for t, w in zip(["点名", "X（北）", "Y（东）", "点名", "X（北）", "Y（东）"], cw):
    put(p, xx + w / 2, yy + 14, t, 8.5, "center")
    xx += w
yy += 20
names = cnet.PTS
rows_xy = [names[i:i + 2] for i in range(0, 9, 2)]
for pair in rows_xy:
    xx = 84
    vals = []
    for nm in pair:
        x, y = cnet.XY[nm]
        vals += [nm, f"{x:.1f}", f"{y:.1f}"]
    while len(vals) < 6:
        vals += ["", "", ""]
    for v, w in zip(vals, cw):
        put(p, xx + w / 2, yy + 14, v, 8.5, "center")
        xx += w
    yy += 20
put(p, 84, yy + 16, "注：QZ1—QZ2—QZ3 位于桥轴线上（Y=0），桥长 800 m；"
    "QN1、QN2 为南引桥点。", 8.5)

yy += 40
put(p, 84, yy, "二、六种方案精度评定结果", 10.5, "left", BLACK)
yy += 8
hdr = ["方案", "固定方式", "r", "方向", "边长", "最弱点", "精度(mm)",
       "最弱边", "中误差(mm)", "相对中误差", "最远点", "中误差(mm)", "相对中误差"]
cwt = [38, 50, 26, 22, 22, 28, 34, 44, 34, 50, 44, 34, 50]
xx = 60
p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cwt), yy + 24), color=BLACK, width=0.8)
for t, w in zip(hdr, cwt):
    put(p, xx + w / 2, yy + 15, t, 7, "center")
    xx += w
yy += 24
for k in ORDER:
    s = SCHEMES[k]
    vals = [k[0], k[1], f"{s['rbar']:.3f}", str(s["nf"]), str(s["nd"]),
            s["wp"], f"{s['mwp']:.3f}", f"{s['we'][0]}–{s['we'][1]}",
            f"{s['swe']:.3f}", f"1/{s['rel']:,.0f}",
            f"{s['lo'][0]}–{s['lo'][1]}", f"{s['lo_sig']:.3f}",
            f"1/{s['lo_rel']:,.0f}"]
    xx = 60
    p.draw_rect(pymupdf.Rect(60, yy, 60 + sum(cwt), yy + 22), color=BLACK,
                width=0.8)
    for v, w in zip(vals, cwt):
        put(p, xx + w / 2, yy + 14, v, 7, "center")
        xx += w
    yy += 22
put(p, 60, yy + 18, "注：r 为平均多余观测分量；最弱点精度为点位中误差 "
    "m=√(mX²+mY²)；相对中误差 = 边长/中误差。", 8)

yy += 44
put(p, 60, yy, "三、观测值精度指标", 10.5, "left", BLACK)
yy += 6
for t in ["方向观测中误差 σ_方向 = 1.8″；边长中误差 σ_S = 2 mm + 2 ppm×S。",
          "环/附合条件按 GNSS 三等网要求检核；优化设计采用间接平差精度评定"
          "（Q = N^-1，N = A'PA）。"]:
    yy += 16
    put(p, 60, yy, t, 8.5)

try:
    out.subset_fonts()
except Exception as e:
    print("subset skip", e)
pdf = os.path.join(OUT, "控制网优化设计（指导书表格填写版）.pdf")
out.save(pdf, garbage=4, deflate=True)
print("saved", pdf, "pages", out.page_count)

# ---------------- Excel ----------------
wb = Workbook()
TH = Side(style="thin", color="000000")
BD = Border(left=TH, right=TH, top=TH, bottom=TH)
F10 = Font(name="宋体", size=10)
FB = Font(name="宋体", size=10, bold=True)
FTT = Font(name="宋体", size=13, bold=True)
FH = PatternFill("solid", fgColor="DCE6F1")
FS = PatternFill("solid", fgColor="E8E8E8")
CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
LFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


def wcell(ws, r, c, v, font=F10, align=CTR, fmt=None, fill=None):
    x = ws.cell(row=r, column=c, value=v)
    x.font = font
    x.alignment = align
    x.border = BD
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill


ws = wb.active
ws.title = "1-控制点坐标"
ws.column_dimensions["A"].width = 12
for col in "BCDE":
    ws.column_dimensions[col].width = 16
ws.merge_cells("A1:C1")
wcell(ws, 1, 1, "桥梁 GNSS 施工控制网点坐标（独立坐标系，m）", FTT)
for j, h in enumerate(["点名", "X（北）", "Y（东）"], 1):
    wcell(ws, 2, j, h, FB, fill=FH)
for i, nm in enumerate(cnet.PTS, 3):
    x, y = cnet.XY[nm]
    wcell(ws, i, 1, nm, FB)
    wcell(ws, i, 2, x, fmt="0.0")
    wcell(ws, i, 3, y, fmt="0.0")

ws2 = wb.create_sheet("2-精度评定汇总")
ws2.column_dimensions["A"].width = 12
for col in "BCDEFGHIJKLM":
    ws2.column_dimensions[col].width = 14
ws2.merge_cells("A1:M1")
wcell(ws2, 1, 1, "控制网模拟优化设计计算结果对比", FTT)
hd = ["方案", "固定方式", "平均多余观测分量", "方向数", "边长数", "最弱点",
      "精度值(mm)", "最弱边", "边长(m)", "中误差(mm)", "相对中误差",
      "最远点边长(m)", "中误差(mm)", "相对中误差"]
for j, h in enumerate(hd, 1):
    wcell(ws2, 2, j, h, FB, fill=FH)
for i, k in enumerate(ORDER, 3):
    s = SCHEMES[k]
    vals = [k[0], k[1], s["rbar"], s["nf"], s["nd"], s["wp"], s["mwp"],
            f"{s['we'][0]}–{s['we'][1]}", s["S"], s["swe"],
            f"1/{s['rel']:,.0f}", s["L"], s["lo_sig"], f"1/{s['lo_rel']:,.0f}"]
    for j, v in enumerate(vals, 1):
        wcell(ws2, i, j, v,
              fmt="0.000" if j in (3, 7, 10, 13) else
              ("0.0" if j in (9, 12) else None))

ws.merge_cells("A13:C13")
_note = ws.cell(row=13, column=1,
                value="说明：本表为独立坐标系（原点 QZ1，X 轴沿桥轴线指向 QZ3）；"
                      "桥位取自湘江湘潭段卫星影像（Esri World Imagery），"
                      "中心约 112.9655°E、27.9169°N。")
_note.font = Font(name="宋体", size=9)
_note.alignment = LFT

ws3 = wb.create_sheet("3-观测方案清单")
ws3.column_dimensions["A"].width = 10
ws3.column_dimensions["B"].width = 10
ws3.column_dimensions["C"].width = 10
ws3.merge_cells("A1:C1")
wcell(ws3, 1, 1, "各方案边长/方向观测清单（“√”为观测）", FTT)
ED = cnet.EDGES0
wcell(ws3, 2, 1, "边长", FB, fill=FH)
wcell(ws3, 2, 2, "初始", FB, fill=FH)
wcell(ws3, 2, 3, "方1-Ⅰ", FB, fill=FH)
wcell(ws3, 2, 4, "方1-Ⅱ", FB, fill=FH)
wcell(ws3, 2, 5, "方2-Ⅰ", FB, fill=FH)
wcell(ws3, 2, 6, "方2-Ⅱ", FB, fill=FH)
sets = {}
for key, js in [("初始", "初始方案"), ("方1-Ⅰ", "方案1_一次优化"),
                ("方1-Ⅱ", "方案1_二次优化"), ("方2-Ⅰ", "方案2_一次优化"),
                ("方2-Ⅱ", "方案2_二次优化")]:
    if js == "初始方案":
        sets[key] = {(min(*e), max(*e)) for e in ED}
    else:
        sets[key] = {(min(*e), max(*e)) for e in RP[js]["edges"]}
for i, e in enumerate(ED, 3):
    wcell(ws3, i, 1, f"{e[0]}–{e[1]}", F10, LFT)
    for j, key in enumerate(["初始", "方1-Ⅰ", "方1-Ⅱ", "方2-Ⅰ", "方2-Ⅱ"], 2):
        wcell(ws3, i, j, "√" if (min(*e), max(*e)) in sets[key] else "")
ws3.column_dimensions["C"].width = 10
for col in "DEF":
    ws3.column_dimensions[col].width = 10

xp = os.path.join(OUT, "控制网优化设计成果.xlsx")
wb.save(xp)
print("saved", xp)
