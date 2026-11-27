# -*- coding: utf-8 -*-
"""建筑物沉降变形测量: 生成 Excel 内业成果 + 手册原表填写版 PDF"""
import math
import os
import sys

import pymupdf
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from settle_data import (H_A, M, LOOP, RING_W, CA_CHECK, SEG_CHK, MON,
                         MON_STATION, PERIOD_LABEL, BENCH, SETTLE, STAB,
                         ring_length, ring_limit, fmt)   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\沉降测量成果"
os.makedirs(OUT, exist_ok=True)
HB = r"C:\Users\31710\OneDrive\Desktop\测量数据\要求\工程测量实习计划及指导书-叶险峰2026.pdf"
FONT = r"C:\Windows\Fonts\simsun.ttc"
INK = (0.03, 0.10, 0.45)
BLACK = (0, 0, 0)
FT = pymupdf.Font(fontfile=FONT)

# =========================== Excel ===========================
wb = Workbook()
THIN = Side(style="thin", color="000000")
BD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FT10 = Font(name="宋体", size=10)
FTB = Font(name="宋体", size=10, bold=True)
FTT = Font(name="宋体", size=14, bold=True)
FILL_H = PatternFill("solid", fgColor="DCE6F1")
FILL_S = PatternFill("solid", fgColor="E8E8E8")
FILL_M = PatternFill("solid", fgColor="FFF2CC")
CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
LFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


def cell(ws, r, c, v, font=FT10, align=CTR, fmt=None, fill=None):
    x = ws.cell(row=r, column=c, value=v)
    x.font = font
    x.alignment = align
    x.border = BD
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill
    return x


def mrg(ws, r1, c1, r2, c2, v, font=FT10, align=CTR, fill=None, h=None):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ws.cell(row=r, column=c).border = BD
    x = ws.cell(row=r1, column=c1, value=v)
    x.font = font
    x.alignment = align
    if fill:
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                ws.cell(row=r, column=c).fill = fill
    if (r1, c1) != (r2, c2):
        ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    if h:
        ws.row_dimensions[r1].height = h


def page(ws):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = 9
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0


# ---- S0 说明 ----
ws = wb.active
ws.title = "说明"
page(ws)
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 100
mrg(ws, 1, 2, 1, 2, "建筑物沉降变形测量  内业成果（三等监测 / 二等水准）", FTT)
r = 3
info = [
    "1. 监测对象：某房屋，4 个沉降监测点 P1～P4（房屋四角）；基准点 A、B、C 构成闭合环，A 为已知点，H_A = 79.568 m。",
    "2. 观测周期：第一期（第 0 天）、第二期（相隔 7 天）、第三期（相隔 14 天）；基准点 A→B→C→A 往返观测，"
    "监测点位于 A→B 附合路线上，往返观测。",
    "3. 限差依据：GB/T 12897—2006《国家一、二等水准测量规范》；"
    "环闭合差限差 W允 = ±4√F（mm，F 为环长 km）；往返测高差不符值限差 = ±4√R（R 为测段长 km，小于 0.1 取 0.1）。",
    "4. 平差方法：基准点闭合环按边长比例配赋闭合差，末边承接修约尾差；监测点高程按 A→B 各小段往返平均长度分配环线改正量。",
    "5. 沉降量：各期高程减去第一期（首次）观测高程，负值表示下沉；沉降速率 = 累计沉降量 / 14 d。",
    "6. 三期环闭合差：+0.3475 mm、-0.4150 mm、+0.1000 mm，均小于限差 ±3.749 / ±3.741 / ±3.738 mm，外业质量合格。",
    "7. 基准点稳定性：两期间高差较差 0.27～0.73 mm，均小于限差，A、B、C 点在本监测期内稳定。",
    "8. 变形结论：P2 累计下沉 -0.9225 mm（最大），P4 -0.3401 mm，P1 +0.1813 mm，P3 +0.1271 mm；"
    "各点沉降速率绝对值 ≤ 0.066 mm/d，房屋处于稳定状态。",
]
for t in info:
    c = ws.cell(row=r, column=2, value=t)
    c.font = FT10
    c.alignment = LFT
    ws.row_dimensions[r].height = 30
    r += 1

# ---- S1 环闭合差配赋 ----
ws = wb.create_sheet("1-基准点环配赋")
page(ws)
for col, w in zip("ABCDEFGH", [8, 14, 12, 14, 13, 14, 14, 12]):
    ws.column_dimensions[col].width = w
mrg(ws, 1, 1, 1, 8, "一、基准点闭合环 A→B→C→A 高差闭合差配赋", FTT, h=30)
r = 3
for p in (1, 2, 3):
    mrg(ws, r, 1, r, 8, f"{PERIOD_LABEL[p]}　环长 {ring_length(p):.3f} m　"
        f"闭合差 W = {RING_W[p]:+.4f} mm　限差 W允 = ±{ring_limit(p):.3f} mm",
        FTB, align=LFT, fill=FILL_S, h=22)
    r += 1
    for j, h in enumerate(["测段", "平均边长(m)", "观测高差中数(mm)", "改正数(mm)",
                           "改正后高差(mm)", "高程(m)", "", ""], 1):
        cell(ws, r, j, h, FTB, fill=FILL_H)
    ws.merge_cells(start_row=r, start_column=6, end_row=r, end_column=8)
    r += 1
    h = (BENCH[p][0], BENCH[p][1], BENCH[p][2], BENCH[p][0])
    cell(ws, r, 1, "A", FTB, fill=FILL_M)
    for j in range(2, 6):
        cell(ws, r, j, "—")
    mrg(ws, r, 6, r, 8, f"{h[0]:.7f}", FTB, fill=FILL_M)
    r += 1
    for i, (nm, L, dh, v, adj) in enumerate(LOOP[p]):
        cell(ws, r, 1, nm, FT10, align=LFT)
        cell(ws, r, 2, L, fmt="0.0000")
        cell(ws, r, 3, dh, fmt="+0.0000;-0.0000;0.0000")
        cell(ws, r, 4, v, fmt="+0.0000;-0.0000;0.0000")
        cell(ws, r, 5, adj, fmt="+0.0000;-0.0000;0.0000")
        mrg(ws, r, 6, r, 8, f"{h[i+1]:.7f}", FT10,
            fill=FILL_M if i == 1 else None)
        r += 1
    cell(ws, r, 1, "Σ", FTB, fill=FILL_S)
    cell(ws, r, 2, ring_length(p), FTB, fmt="0.0000", fill=FILL_S)
    cell(ws, r, 3, RING_W[p], FTB, fmt="+0.0000;-0.0000;0.0000", fill=FILL_S)
    cell(ws, r, 4, -RING_W[p], FTB, fmt="+0.0000;-0.0000;0.0000", fill=FILL_S)
    cell(ws, r, 5, 0.0, FTB, fmt="0.0000", fill=FILL_S)
    mrg(ws, r, 6, r, 8, f"{H_A:.7f}", FTB, fill=FILL_S)
    r += 1
    mrg(ws, r, 1, r, 8, f"检核：三边改正后高差之和 = 0.0000 mm；"
        f"B、C 高程 = {h[1]:.7f}、{h[2]:.7f} m；闭合至 A 较差 0.0000 mm。",
        FT10, align=LFT, h=20)
    r += 2

# ---- S2 基准点高程成果 ----
ws = wb.create_sheet("2-基准点成果")
page(ws)
for col, w in zip("ABCDEFG", [12, 16, 16, 16, 16, 16, 16]):
    ws.column_dimensions[col].width = w
mrg(ws, 1, 1, 1, 7, "二、基准点高程成果与稳定性", FTT, h=30)
r = 3
for j, h in enumerate(["点名", "第一期(m)", "第二期(m)", "第三期(m)",
                       "2期-1期(mm)", "3期-2期(mm)", "3期-1期(mm)"], 1):
    cell(ws, r, j, h, FTB, fill=FILL_H)
r += 1
for i, nm in enumerate(["A", "B", "C"]):
    cell(ws, r, 1, nm, FTB, fill=FILL_M)
    for k in range(3):
        cell(ws, r, 2 + k, BENCH[k + 1][i], fmt="0.0000000")
    for k, (a, b) in enumerate([(1, 2), (2, 3), (1, 3)]):
        d = (BENCH[b][i] - BENCH[a][i]) * M
        cell(ws, r, 5 + k, d, fmt="+0.0000;-0.0000;0.0000")
    r += 1
mrg(ws, r, 1, r, 7, "A 为已知点（79.568 m），其高程变化值为 0。", FT10, align=LFT, h=20)
r += 2
mrg(ws, r, 1, r, 7, "基准点间高差较差与稳定性判定（限差取 2√2·μ√L，μ = 2 mm/√km）",
    FTB, align=LFT, fill=FILL_S, h=22)
r += 1
for j, h in enumerate(["测段", "平均边长(m)", "2期-1期(mm)", "3期-2期(mm)",
                       "3期-1期(mm)", "限差(mm)", "判定"], 1):
    cell(ws, r, j, h, FTB, fill=FILL_H)
r += 1
for s in STAB:
    cell(ws, r, 1, s["name"], FT10)
    cell(ws, r, 2, s["L"], fmt="0.000")
    cell(ws, r, 3, s["d12"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 4, s["d23"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 5, s["d13"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 6, s["lim"], fmt="0.000")
    ok = max(abs(s["d12"]), abs(s["d23"]), abs(s["d13"])) <= s["lim"]
    cell(ws, r, 7, "稳定" if ok else "超限", FT10, fill=FILL_M)
    r += 1
mrg(ws, r, 1, r, 7, "结论：各基准点间高差较差最大 0.7281 mm，远小于限差，"
    "三个基准点在本监测期内稳定，可作为沉降监测的起算依据。", FT10, align=LFT, h=34)

# ---- S3 监测点高程与沉降量 ----
ws = wb.create_sheet("3-监测点成果")
page(ws)
for col, w in zip("ABCDEFGHI", [8, 15, 15, 15, 12, 12, 12, 12, 14]):
    ws.column_dimensions[col].width = w
mrg(ws, 1, 1, 1, 9, "三、变形监测点高程成果与沉降量计算", FTT, h=30)
r = 3
for j, h in enumerate(["点号", "第1期(m)", "第2期(m)", "第3期(m)",
                       "第一周(mm)", "第二周(mm)", "累计(mm)", "速率(mm/d)",
                       "对应往测站"], 1):
    cell(ws, r, j, h, FTB, fill=FILL_H)
r += 1
for k in ["P1", "P2", "P3", "P4"]:
    d = SETTLE[k]
    cell(ws, r, 1, k, FTB, fill=FILL_M)
    for j, v in enumerate([d["h1"], d["h2"], d["h3"]]):
        cell(ws, r, 2 + j, v, fmt="0.0000000")
    cell(ws, r, 5, d["d1"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 6, d["d2"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 7, d["cum"], fmt="+0.0000;-0.0000;0.0000",
         fill=FILL_M if abs(d["cum"]) > 0.5 else None)
    cell(ws, r, 8, d["rate"], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 9, MON_STATION[k][0], align=LFT)
    r += 1
mrg(ws, r, 1, r, 9, "注：变化量 = 本期高程 − 上期高程；累计 = 第 3 期 − 第 1 期（负值表示下沉）；"
    "速率 = 累计 / 14 d。", FT10, align=LFT, h=20)
r += 2
mrg(ws, r, 1, r, 9, "沉降过程曲线数据（供作图）", FTB, align=LFT, fill=FILL_S, h=22)
r += 1
cell(ws, r, 1, "期次", FTB, fill=FILL_H)
for j, k in enumerate(["P1", "P2", "P3", "P4"]):
    cell(ws, r, 2 + j, k, FTB, fill=FILL_H)
r += 1
chart_start = r
for i, lab in enumerate(["第一期", "第二期", "第三期"]):
    cell(ws, r, 1, lab, FT10)
    for j, k in enumerate(["P1", "P2", "P3", "P4"]):
        d = SETTLE[k]
        v = [0.0, d["d1"], d["cum"]][i]
        cell(ws, r, 2 + j, v, fmt="0.0000")
    r += 1
chart_end = r - 1

ch = LineChart()
ch.title = "变形监测点累积沉降过程曲线"
ch.y_axis.title = "累积沉降量 (mm)"
ch.x_axis.title = "观测期次"
ch.height = 10
ch.width = 19
data = Reference(ws, min_col=2, max_col=5, min_row=chart_start - 1,
                 max_row=chart_end)
cats = Reference(ws, min_col=1, min_row=chart_start, max_row=chart_end)
ch.add_data(data, titles_from_data=True)
ch.set_categories(cats)
for s in ch.series:
    s.marker.symbol = "circle"
    s.smooth = False
ws.add_chart(ch, f"A{r + 2}")

# ---- S4 观测质量汇总 ----
ws = wb.create_sheet("4-观测质量汇总")
page(ws)
for col, w in zip("ABCDEFG", [8, 12, 16, 16, 12, 12, 12]):
    ws.column_dimensions[col].width = w
mrg(ws, 1, 1, 1, 7, "四、往返测高差不符值与限差汇总（单位 mm）", FTT, h=30)
r = 3
for j, h in enumerate(["期次", "测段", "往测高差", "返测高差", "不符值",
                       "限差 ±", "判定"], 1):
    cell(ws, r, j, h, FTB, fill=FILL_H)
r += 1
for p in (1, 2, 3):
    for nm, ret, hw, hr, de, lim in SEG_CHK[p]:
        cell(ws, r, 1, f"第{p}期" if nm == "1–8" else "", FT10)
        cell(ws, r, 2, f"往{nm} / 返{ret}", align=LFT)
        cell(ws, r, 3, hw, fmt="+0.000;-0.000;0.000")
        cell(ws, r, 4, hr, fmt="+0.000;-0.000;0.000")
        cell(ws, r, 5, de, fmt="+0.000;-0.000;0.000")
        cell(ws, r, 6, lim, fmt="0.000")
        cell(ws, r, 7, "合格" if abs(de) <= lim else "超限")
        r += 1
    c = CA_CHECK[p]
    cell(ws, r, 2, "C→A 补测段", align=LFT)
    cell(ws, r, 3, c[0], fmt="+0.000;-0.000;0.000")
    cell(ws, r, 4, c[1], fmt="+0.000;-0.000;0.000")
    cell(ws, r, 5, c[2], fmt="+0.000;-0.000;0.000")
    cell(ws, r, 6, c[3], fmt="0.000")
    cell(ws, r, 7, "合格")
    r += 1
    cell(ws, r, 2, "环闭合差", align=LFT)
    cell(ws, r, 3, "—")
    cell(ws, r, 4, "—")
    cell(ws, r, 5, RING_W[p], fmt="+0.0000;-0.0000;0.0000")
    cell(ws, r, 6, ring_limit(p), fmt="0.000")
    cell(ws, r, 7, "合格", fill=FILL_M)
    r += 1

# ---- S5 稳定性与结论 ----
ws = wb.create_sheet("5-稳定性与结论")
page(ws)
ws.column_dimensions["A"].width = 3
ws.column_dimensions["B"].width = 108
mrg(ws, 1, 2, 1, 2, "五、基准点稳定性分析与变形结论", FTT, h=30)
r = 3
txt = [
    "（一）基准点稳定性分析",
    "  基准点稳定性以两期观测所得同名点间高差较差判定。取每公里高差中数中误差 μ = 2 mm/√km"
    "（由二等水准环闭合差限差 4√F 反算），两期高差较差的限差为 2√2·μ√L。",
]
for s in STAB:
    txt.append(f"  {s['name']}：平均边长 {s['L']:.3f} m，限差 ±{s['lim']:.3f} mm；"
               f"较差（2期-1期）{s['d12']:+.4f} mm、（3期-2期）{s['d23']:+.4f} mm、"
               f"（3期-1期）{s['d13']:+.4f} mm。")
txt += [
    "  各较差均远小于限差，说明三个基准点在本监测期内没有发生显著变化，可作为沉降监测的起算依据。",
    "  同时，三期环闭合差（+0.3475、-0.4150、+0.1000 mm）均小于限差（±3.749、±3.741、±3.738 mm），"
    "说明基准点观测成果本身可靠。",
    "",
    "（二）变形监测点沉降分析",
    "  P1：+0.2342 → -0.0529 mm，累计 +0.1813 mm，呈轻微回弹；",
    "  P2：-0.1838 → -0.7387 mm，累计 -0.9225 mm，为本次监测中沉降最大点，第二周沉降明显；",
    "  P3：-0.0937 → +0.2208 mm，累计 +0.1271 mm，先降后升；",
    "  P4：-0.0522 → -0.2879 mm，累计 -0.3401 mm，持续小幅下沉。",
    "  各点沉降速率绝对值 0.009～0.066 mm/d，均小于 0.1 mm/d，房屋整体处于稳定状态；"
    "P2 点累计沉降最大（不足 1 mm），建议后续周期重点观测。",
    "",
    "（三）观测质量评述",
    "  1. 往返测高差不符值：三期各测段均小于 ±4√R 限差，全程不符值 -1.445、-0.440、+1.430 mm "
    "分别小于 ±2.714、±2.704、±2.697 mm，合格；",
    "  2. 环闭合差：三期均小于 ±4√F 限差，合格；",
    "  3. 视距与读数：最大单站视距差 1.005 m、最大累积视距差 2.264 m、两次高差之差最大 0.21 mm，"
    "满足二等水准要求；",
    "  4. C–A 补测段往返各 20 站，不符值 0.250～0.320 mm，均小于 ±2.589 mm，合格。",
]
for t in txt:
    c = ws.cell(row=r, column=2, value=t)
    c.font = FTB if t.startswith("（") else FT10
    c.alignment = LFT
    ws.row_dimensions[r].height = 18 if t else 8
    r += 1

xp = os.path.join(OUT, "建筑物沉降观测内业成果.xlsx")
wb.save(xp)
print("saved", xp)

# =========================== PDF ===========================
src = pymupdf.open(HB)
out = pymupdf.open()


def new_page():
    p = out.new_page(width=595.3, height=841.9)
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


def cellc(p, x0, x1, yc, t, size=9, color=INK, dy=3.0):
    s = size
    while s > 6 and FT.text_length(t, fontsize=s) > (x1 - x0) - 3:
        s -= 0.2
    put(p, (x0 + x1) / 2, yc + dy, t, size=s, align="center", color=color)


# ---------- 封面 ----------
p = new_page()
p.draw_rect(pymupdf.Rect(56, 66, 539, 300), color=BLACK, width=1.2)
put(p, 297.6, 130, "《 工 程 测 量 实 习 》", 22, "center", BLACK)
put(p, 297.6, 172, "建筑物沉降变形测量（必做）", 17, "center", BLACK)
put(p, 297.6, 208, "内 业 成 果", 17, "center", BLACK)
put(p, 297.6, 248, "（按指导书第 25～26 页原表填写）", 11, "center", BLACK)
put(p, 297.6, 276, "二〇二六年十一月", 11, "center", BLACK)
rows = [("学　　院", "土木工程学院"), ("专　　业", "测绘工程"),
        ("班　　级", "2 班"), ("学　　号", "202305801025"),
        ("姓　　名", ""), ("组　　号", ""), ("指导教师", "叶险峰")]
y0 = 322
p.draw_rect(pymupdf.Rect(140, y0, 460, y0 + 24 * len(rows)), color=BLACK,
            width=0.8)
for i, (k, v) in enumerate(rows):
    yy = y0 + 24 * i
    if i:
        p.draw_line((140, yy), (460, yy), color=BLACK, width=0.8)
    p.draw_line((215, yy), (215, yy + 24), color=BLACK, width=0.8)
    put(p, 177, yy + 16, k, 10.5, "center", BLACK)
    put(p, 225, yy + 16, v, 10.5, "left", BLACK)
y = 520
put(p, 84, y, "一、监测概况", 11.5, "left", BLACK)
y += 20
for t in [
    "监测对象：某房屋，布设 4 个沉降监测点 P1～P4（房屋四角）；基准点 A、B、C 组成闭合环。",
    "已知点：A，H_A = 79.568 m。等级：三等监测，按二等水准精度施测。",
    "观测路线：往测 A→B→C（22 站），返测 C→A（20 站），闭合环长 878.413 m；"
    "监测点位于 A→B 边上。",
    "观测周期：第一期（第 0 天）、第二期（相隔 7 天）、第三期（相隔 14 天）。",
]:
    put(p, 84, y, t, 9.5, "left", BLACK)
    y += 17
y += 8
put(p, 84, y, "二、主要成果", 11.5, "left", BLACK)
y += 20
for t in [
    f"基准点高程（第三期）：A = {BENCH[3][0]:.7f} m，B = {BENCH[3][1]:.7f} m，"
    f"C = {BENCH[3][2]:.7f} m；",
    "三期环闭合差：+0.3475、-0.4150、+0.1000 mm；限差：±3.749、±3.741、±3.738 mm；",
    "基准点间高差较差最大 0.7281 mm，小于限差，基准点稳定；",
    "监测点累计沉降：P1 +0.1813 mm，P2 -0.9225 mm，P3 +0.1271 mm，P4 -0.3401 mm。",
]:
    put(p, 84, y, t, 9.5, "left", BLACK)
    y += 17
y += 8
put(p, 84, y, "三、本册内容", 11.5, "left", BLACK)
y += 20
for t in [
    "第 2 页：指导书第 25 页原表（6. 高程误差配赋表、7. 基准点成果表）；",
    "第 3 页：指导书第 26 页原表（8. 变形监测点成果表）；",
    "第 4～6 页：附表（二、三期配赋；往返测高差不符值汇总；稳定性分析与沉降量汇总）；",
    "第 7 页：附图（沉降过程曲线、点位布设与观测路线示意图）。",
]:
    put(p, 84, y, t, 9.5, "left", BLACK)
    y += 17

# ---------- 手册 p25: 配赋表 + 基准点成果表 ----------
p = hb(25)
COL = [(84.80, 114.75), (114.75, 185.60), (185.60, 266.25), (266.25, 332.25),
       (332.25, 447.60), (447.60, 510.50)]
ROW_OUT = [151.14, 179.49, 217.49, 255.49]     # 点名/高程列半格中心
ROW_MID = [160.64, 198.49, 236.49]             # 距离~改正后高差列行中心
SUM_ROW = 310.62
names = ["A", "B", "C", "A"]
heights = [H_A, BENCH[1][1], BENCH[1][2], H_A]
for yc, nm, hv in zip(ROW_OUT, names, heights):
    cellc(p, *COL[0], yc, nm, 9.2)
    cellc(p, *COL[5], yc, f"{hv:.7f}", 8.6)
for yc, (nm, L, dh, v, adj) in zip(ROW_MID, LOOP[1]):
    cellc(p, *COL[1], yc, f"{L:.3f}", 8.6)
    cellc(p, *COL[2], yc, f"{dh:+.4f}", 8.6)
    cellc(p, *COL[3], yc, f"{v:+.4f}", 8.6)
    cellc(p, *COL[4], yc, f"{adj:+.4f}", 8.6)
for (x0, x1), v in zip(COL[1:5], [f"{ring_length(1):.3f}", f"{RING_W[1]:+.4f}",
                                  f"{-RING_W[1]:+.4f}", "0.0000"]):
    cellc(p, x0, x1, SUM_ROW, v, 8.6)
put(p, 120, 348.2, f"{RING_W[1]:+.4f} mm", 9)
put(p, 345, 348.2, f"±{ring_limit(1):.3f} mm", 9)

# 略图: A-B-C 三角形（避开"略图："字样）
x0, x1 = 84.6, 510.7
sc = 0.80
ox, oy = 122, 430
Ax, Ay = ox, oy
Bx, By = ox + 367.19 * sc, oy
Cx, Cy = ox + 409.6 * sc, oy - 83.0 * sc
p.draw_line((Ax, Ay), (Bx, By), color=BLACK, width=1.1)
p.draw_line((Bx, By), (Cx, Cy), color=BLACK, width=1.1)
p.draw_line((Cx, Cy), (Ax, Ay), color=BLACK, width=1.1)
for (xx, yy), lab in [((Ax, Ay), "A"), ((Bx, By), "B"), ((Cx, Cy), "C")]:
    p.draw_circle((xx, yy), 2.5, color=BLACK, width=1.0)
    put(p, xx - 8, yy - 6, lab, 9.5)
put(p, (Ax + Bx) / 2 - 13, Ay + 14, "367.190", 8)
put(p, (Bx + Cx) / 2 + 6, (By + Cy) / 2 + 2, "93.300", 8)
put(p, (Ax + Cx) / 2 - 46, (Ay + Cy) / 2 - 3, "417.923", 8)
put(p, (Ax + Bx) / 2 - 26, Ay + 28, "P4   P3   P2   P1", 8)
put(p, Ax + 5, Ay + 16, f"{H_A:.3f}", 8)
put(p, Bx - 22, By + 18, f"{BENCH[1][1]:.3f}", 8)
put(p, Cx + 5, Cy - 2, f"{BENCH[1][2]:.3f}", 8)

# 基准点成果表 6 行
BC = [(78.35, 154.50), (154.50, 221.25), (221.25, 302.30), (302.30, 516.90)]
BR = [624.79, 649.29, 673.79, 698.29, 722.79, 747.29]
seq = [("A", 1), ("B", 1), ("C", 1), ("A", 2), ("B", 2), ("C", 2)]
idx = {"A": 0, "B": 1, "C": 2}
for yc, (nm, per) in zip(BR, seq):
    put(p, (BC[0][0] + BC[0][1]) / 2, yc + 3, f"{nm}（第{per}期）", 9,
        "center")
    cellc(p, *BC[1], yc, "二等", 9)
    put(p, (BC[2][0] + BC[2][1]) / 2, yc + 3, f"{BENCH[per][idx[nm]]:.7f}",
        8.6, "center")
# 示意图(小三角)
sx0, sx1, sy0, sy1 = 310, 510, 592, 756
sc2 = min((sx1 - sx0 - 30) / 470.0, (sy1 - sy0 - 50) / 120.0)
ox2, oy2 = sx0 + 15, sy1 - 30
p.draw_line((ox2, oy2), (ox2 + 367.19 * sc2, oy2), color=BLACK, width=0.9)
p.draw_line((ox2 + 367.19 * sc2, oy2), (ox2 + 409.6 * sc2, oy2 - 83 * sc2),
            color=BLACK, width=0.9)
p.draw_line((ox2 + 409.6 * sc2, oy2 - 83 * sc2), (ox2, oy2), color=BLACK,
            width=0.9)
for (xx, yy), lab in [((ox2, oy2), "A"), ((ox2 + 367.19 * sc2, oy2), "B"),
                      ((ox2 + 409.6 * sc2, oy2 - 83 * sc2), "C")]:
    p.draw_circle((xx, yy), 2.2, color=BLACK, width=0.9)
    put(p, xx + 3, yy + 8, lab, 8)
put(p, sx0 + 4, sy0 + 14, "两期高差变化（2期-1期）：", 8)
put(p, sx0 + 4, sy0 + 28, "A→B  +0.7281 mm", 8)
put(p, sx0 + 4, sy0 + 40, "A→C  +0.4614 mm", 8)
put(p, sx0 + 4, sy0 + 52, "B→C  -0.2667 mm", 8)
put(p, sx0 + 4, sy0 + 66, "均小于限差，基准点稳定", 8)

# ---------- 手册 p26: 变形监测点成果表 ----------
p = hb(26)
MC = [(87.20, 163.25), (163.25, 255.10), (255.10, 508.05)]
MR = [140.19 + 24.5 * i for i in range(12)]
order = []
for k in ["P1", "P2", "P3", "P4"]:
    for per in (1, 2, 3):
        order.append((k, per))
for yc, (k, per) in zip(MR, order):
    put(p, (MC[0][0] + MC[0][1]) / 2, yc + 3, f"{k}（第{per}期）", 9,
        "center")
    put(p, (MC[1][0] + MC[1][1]) / 2, yc + 3, f"{MON[k][per-1]:.7f}", 8.6,
        "center")
# 示意图: 房屋 + 4 点
bx0, bx1, by0, by1 = 262, 500, 134, 416
p.draw_rect(pymupdf.Rect(bx0 + 40, by0 + 40, bx1 - 40, by1 - 40), color=BLACK,
            width=1.0)
put(p, (bx0 + bx1) / 2, by0 + 30, "被监测房屋", 8, "center")
pp = {"P1": (bx1 - 48, by1 - 48), "P2": (bx1 - 48, by0 + 48),
      "P3": (bx0 + 48, by0 + 48), "P4": (bx0 + 48, by1 - 48)}
for k, (xx, yy) in pp.items():
    p.draw_circle((xx, yy), 2.6, color=BLACK, width=0.9)
    put(p, xx + 4, yy + 3, k, 8.5)
put(p, (bx0 + bx1) / 2, by1 - 18,
    "P1、P2 位于房屋东侧，P3、P4 位于西侧", 7.5, "center")

# ---------- 附表1: 二三期配赋 ----------
p = new_page()
put(p, 297.6, 66, "附表 1　第二、三期高程误差配赋表", 15, "center", BLACK)
yy = 96
for per in (2, 3):
    put(p, 84, yy, f"{PERIOD_LABEL[per]}　环长 {ring_length(per):.3f} m　"
        f"W = {RING_W[per]:+.4f} mm　W允 = ±{ring_limit(per):.3f} mm", 10)
    yy += 10
    hdr = ["测段", "平均边长(m)", "观测高差中数(mm)", "改正数(mm)",
           "改正后高差(mm)", "高程(m)"]
    cw = [72, 84, 92, 76, 92, 84]
    xx = 84
    p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cw), yy + 22), color=BLACK,
                width=0.8)
    for h, w in zip(hdr, cw):
        put(p, xx + w / 2, yy + 15, h, 8, "center")
        xx += w
    yy += 22
    p.draw_rect(pymupdf.Rect(84, yy, 84 + sum(cw), yy + 22 * 5), color=BLACK,
                width=0.8)
    rowsT = [("A", "—", "—", "—", "—", f"{H_A:.7f}")]
    _hs2 = [H_A, BENCH[per][1], BENCH[per][2], H_A]
    for i, (nm, L, dh, v, adj) in enumerate(LOOP[per]):
        rowsT.append((nm.replace(" → ", "→"), f"{L:.4f}", f"{dh:+.4f}",
                      f"{v:+.4f}", f"{adj:+.4f}", f"{_hs2[i+1]:.7f}"))
    rowsT.append(("Σ", f"{ring_length(per):.4f}", f"{RING_W[per]:+.4f}",
                  f"{-RING_W[per]:+.4f}", "0.0000", f"{H_A:.7f}"))
    for rowv in rowsT:
        xx = 84
        for v, w in zip(rowv, cw):
            put(p, xx + w / 2, yy + 15, v, 8, "center")
            xx += w
        yy += 22
    yy += 18

# 观测质量摘要
put(p, 84, yy + 10, "往返测高差不符值汇总（mm）", 11)
yy += 24
hdr = ["期次", "往测高差", "返测高差", "不符值", "限差", "判定"]
cw = [60, 92, 92, 76, 76, 60]
xx = 84
p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cw), yy + 20), color=BLACK, width=0.8)
for h, w in zip(hdr, cw):
    put(p, xx + w / 2, yy + 14, h, 8, "center")
    xx += w
yy += 20
for per in (1, 2, 3):
    row = SEG_CHK[per][-1]
    vals = [f"第{per}期", f"{row[2]:+.3f}", f"{row[3]:+.3f}", f"{row[4]:+.3f}",
            f"±{row[5]:.3f}", "合格"]
    xx = 84
    p.draw_rect(pymupdf.Rect(84, yy, 84 + sum(cw), yy + 20), color=BLACK,
                width=0.8)
    for v, w in zip(vals, cw):
        put(p, xx + w / 2, yy + 14, v, 8, "center")
        xx += w
    yy += 20
put(p, 84, yy + 20, "C–A 补测段：不符值 +0.250 / -0.280 / +0.320 mm，"
    "均小于 ±2.589 mm，合格。", 9)
put(p, 84, yy + 38, "环闭合差：+0.3475 / -0.4150 / +0.1000 mm，"
    "限差 ±3.749 / ±3.741 / ±3.738 mm，全部合格。", 9)

# ---------- 附表2: 稳定性 + 沉降量 ----------
p = new_page()
put(p, 297.6, 66, "附表 2　基准点稳定性分析与沉降量汇总", 15, "center", BLACK)
put(p, 84, 96, "一、基准点间高差较差（限差 2√2·μ√L，μ = 2 mm/√km）", 11)
yy = 106
hdr = ["测段", "平均边长(m)", "2期-1期", "3期-2期", "3期-1期", "限差", "判定"]
cw = [66, 72, 62, 62, 62, 56, 46]
xx = 84
p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cw), yy + 20), color=BLACK, width=0.8)
for h, w in zip(hdr, cw):
    put(p, xx + w / 2, yy + 14, h, 8, "center")
    xx += w
yy += 20
for s in STAB:
    vals = [s["name"], f"{s['L']:.3f}", f"{s['d12']:+.4f}", f"{s['d23']:+.4f}",
            f"{s['d13']:+.4f}", f"±{s['lim']:.3f}", "稳定"]
    xx = 84
    p.draw_rect(pymupdf.Rect(84, yy, 84 + sum(cw), yy + 20), color=BLACK,
                width=0.8)
    for v, w in zip(vals, cw):
        put(p, xx + w / 2, yy + 14, v, 8, "center")
        xx += w
    yy += 20
put(p, 84, yy + 18, "结论：各基准点间高差较差最大 0.7281 mm，远小于限差，"
    "三个基准点在本监测期内稳定。", 9)
yy += 34
put(p, 84, yy, "二、变形监测点高程与沉降量", 11)
yy += 12
hdr = ["点号", "第1期(m)", "第2期(m)", "第3期(m)", "第一周(mm)", "第二周(mm)",
       "累计(mm)", "速率(mm/d)"]
cw = [34, 62, 62, 62, 52, 52, 52, 50]
xx = 84
p.draw_rect(pymupdf.Rect(xx, yy, xx + sum(cw), yy + 22), color=BLACK, width=0.8)
for h, w in zip(hdr, cw):
    put(p, xx + w / 2, yy + 15, h, 8, "center")
    xx += w
yy += 22
for k in ["P1", "P2", "P3", "P4"]:
    d = SETTLE[k]
    vals = [k, f"{d['h1']:.7f}", f"{d['h2']:.7f}", f"{d['h3']:.7f}",
            f"{d['d1']:+.4f}", f"{d['d2']:+.4f}", f"{d['cum']:+.4f}",
            f"{d['rate']:+.4f}"]
    xx = 84
    p.draw_rect(pymupdf.Rect(84, yy, 84 + sum(cw), yy + 20), color=BLACK,
                width=0.8)
    for v, w in zip(vals, cw):
        put(p, xx + w / 2, yy + 14, v, 8, "center")
        xx += w
    yy += 20
put(p, 84, yy + 18, "注：变化量 = 本期高程 - 上期高程；累计 = 第 3 期 - 第 1 期"
    "（负值表示下沉）；速率 = 累计 / 14 d。", 8.2)
put(p, 84, yy + 40, "三、观测质量评述", 11)
for i, t in enumerate([
    "1. 三期环闭合差 +0.3475、-0.4150、+0.1000 mm，均小于限差 ±3.749、±3.741、±3.738 mm；",
    "2. 六测段往返测高差不符值最大值 1.260 mm，小于 ±4√R 限差；全程不符值最大 1.445 mm，合格；",
    "3. 最大单站视距差 1.005 m、最大累积视距差 2.264 m、两次高差之差最大 0.21 mm；",
    "4. C–A 补测段往返各 20 站，不符值 0.250～0.320 mm，小于 ±2.589 mm，合格。",
]):
    put(p, 84, yy + 58 + i * 16, t, 9)

# ---------- 附图 ----------
p = new_page()
put(p, 297.6, 60, "附图　沉降过程曲线与观测路线示意图", 14, "center", BLACK)
f1 = os.path.join(OUT, "沉降过程曲线图.png")
f2 = os.path.join(OUT, "观测路线示意图.png")
if os.path.exists(f1):
    r1 = pymupdf.Rect(50, 78, 545, 78 + 495 * 0.42)
    p.insert_image(r1, filename=f1)
if os.path.exists(f2):
    r2 = pymupdf.Rect(50, 380, 545, 380 + 495 * 0.62)
    p.insert_image(r2, filename=f2)

try:
    out.subset_fonts()
except Exception as e:
    print("subset skip", e)
path = os.path.join(OUT, "建筑物沉降观测内业成果（手册表格填写版）.pdf")
out.save(path, garbage=4, deflate=True)
print("saved", path, "pages", out.page_count)
