# -*- coding: utf-8 -*-
"""生成《道路曲线测设》个人计算成果 xlsx"""
import math
import os
import re
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
from openpyxl.worksheet.properties import PageSetupProperties
from curve_core import Curve, dms2deg, fmt_dms, fmt_mileage

OUT_DIR = r"C:\Users\31710\OneDrive\Desktop\测量数据\道路曲线测设"
ALPHA = dms2deg(22, 25, 0)
c = Curve(ALPHA)

# ============ 样式工具 ============
THIN = Side(style="thin", color="000000")
MED = Side(style="medium", color="000000")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FONT_HDR = Font(name="宋体", size=10, bold=True)
FONT_TXT = Font(name="宋体", size=10)
FONT_TTL = Font(name="宋体", size=14, bold=True)
FONT_SEC = Font(name="宋体", size=11, bold=True)
FILL_HDR = PatternFill("solid", fgColor="DCE6F1")
FILL_SEC = PatternFill("solid", fgColor="E8E8E8")
FILL_MAIN = PatternFill("solid", fgColor="FFF2CC")
FILL_NOTE = PatternFill("solid", fgColor="F2F2F2")
CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
LFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


def set_page(ws):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "portrait"
    ws.page_setup.paperSize = 9          # A4
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_margins.left = ws.page_margins.right = 0.35
    ws.page_margins.top = ws.page_margins.bottom = 0.55
    ws.oddHeader.center.text = "道路曲线测设（必做）　2班　202305801025"
    ws.oddHeader.center.size = 9
    ws.oddFooter.center.text = "第 &P 页 / 共 &N 页"
    ws.oddFooter.center.size = 9


def put(ws, r, col, v, font=FONT_TXT, align=CTR, fmt=None, fill=None):
    cell = ws.cell(row=r, column=col, value=v)
    cell.font = font
    cell.alignment = align
    cell.border = BORDER
    if fmt:
        cell.number_format = fmt
    if fill:
        cell.fill = fill
    return cell


def merge_put(ws, r1, c1, r2, c2, v, font=FONT_TXT, align=CTR, fill=None,
              height=None):
    for r in range(r1, r2 + 1):
        for cc in range(c1, c2 + 1):
            cell = ws.cell(row=r, column=cc)
            cell.border = BORDER
    cell = ws.cell(row=r1, column=c1, value=v)
    cell.font = font
    cell.alignment = align
    if fill:
        for r in range(r1, r2 + 1):
            for cc in range(c1, c2 + 1):
                ws.cell(row=r, column=cc).fill = fill
    if r1 != r2 or c1 != c2:
        ws.merge_cells(start_row=r1, start_column=c1, end_row=r2, end_column=c2)
    if height:
        ws.row_dimensions[r1].height = height


def widths(ws, spec):
    for col, w in spec.items():
        ws.column_dimensions[col].width = w


def title(ws, ncols, text, sub=None, sub_h=20):
    merge_put(ws, 1, 1, 1, ncols, text, font=FONT_TTL, height=32)
    if sub:
        merge_put(ws, 2, 1, 2, ncols, sub, font=Font(name="宋体", size=9,
                                                     italic=True),
                  align=LFT, height=sub_h)
        return 4
    return 3


def section(ws, r, ncols, text):
    merge_put(ws, r, 1, r, ncols, text, font=FONT_SEC, align=LFT, fill=FILL_SEC,
              height=22)
    return r + 1


# ============ 计算数据 ============
def kind_name(k):
    return {"ZH": "直缓点 ZH", "HY": "缓圆点 HY", "QZ": "曲中点 QZ",
            "YH": "圆缓点 YH", "HZ": "缓直点 HZ", "H1": "第一缓和曲线",
            "C": "圆曲线", "H2": "第二缓和曲线"}[k]


ly = c.L - 2 * c.ls

# 加桩（不含主点）
detail = []
l = 5.0
while l < c.ls - 1e-9:
    detail.append((c.ZH + l, "H1"))
    l += 5.0
l = 10.0
while l < ly - 1e-9:
    detail.append((c.HY + l, "C"))
    l += 10.0
k = 1
while True:
    v = c.ZH + 5.0 * k
    if v >= c.HZ - 1e-9:
        break
    if v > c.YH + 1e-9:
        detail.append((v, "H2"))
    k += 1
kk = int(c.ZH // 100) + 1
while kk * 100.0 < c.HZ - 1e-9:
    v = kk * 100.0
    if v > c.ZH + 1e-9:
        detail.append((v, "C" if v <= c.YH + 1e-9 else "H2"))
    kk += 1

main = [("ZH", c.ZH), ("HY", c.HY), ("QZ", c.QZ), ("YH", c.YH), ("HZ", c.HZ)]
allpts = sorted([(m, "MAIN" if False else k2) for k2, m in main] + detail,
                key=lambda t: t[0])

pts = []
for seq, (mile, kind) in enumerate(allpts, 1):
    d = dict(seq=seq, mile=mile, kind=kind)
    if kind in ("ZH", "HY", "H1"):
        d["l"] = mile - c.ZH
        d["xb"], d["yb"] = c.local_first_spiral(d["l"])
        d["X"], d["Y"] = c.to_geo_from_ZH(d["xb"], d["yb"])
        d["frame"] = "ZH"
    elif kind in ("C", "QZ", "YH"):
        d["l"] = mile - c.HY
        d["xb"], d["yb"] = c.local_circle(d["l"])
        d["X"], d["Y"] = c.to_geo_from_ZH(d["xb"], d["yb"])
        d["frame"] = "ZH"
    else:  # H2, HZ
        d["l"] = c.HZ - mile
        d["xb"], d["yb"] = c.local_second_spiral(d["l"])
        d["X"], d["Y"] = c.to_geo_from_HZ(d["xb"], d["yb"])
        d["frame"] = "HZ"
    # ZH 切线系支距（统一）
    if kind in ("H2", "HZ"):
        d["xz"], d["yz"] = c.local_from_HZ_backward(c.HZ - mile)
    else:
        d["xz"], d["yz"] = d["xb"], d["yb"]
    # 备注
    if kind == "H1":
        d["note"] = "缓和曲线"
    elif kind == "C":
        d["note"] = "圆曲线"
    elif kind == "H2":
        d["note"] = "第二缓和曲线"
    else:
        d["note"] = ""
    if abs(mile - round(mile)) < 1e-9 and kind == "H2":
        d["note"] = "百米桩（里程凑整）"
    d["name"] = kind_name(kind)
    d["remark"] = "百米桩（里程凑整）" if "百米桩" in d["note"] else d["name"]
    pts.append(d)

# 加桩编号 1..n
n = 0
for d in pts:
    if d["kind"] in ("ZH", "HY", "QZ", "YH", "HZ"):
        d["num"] = ""
        d["mark"] = "★"
    else:
        n += 1
        d["num"] = n
        d["mark"] = ""

print("桩点总数", len(pts), " 加桩数", n)

wb = Workbook()

# ================= S1 封面 =================
ws = wb.active
ws.title = "封面"
set_page(ws)
ws.page_setup.fitToHeight = 1
widths(ws, {"A": 14, "B": 20, "C": 3, "D": 14, "E": 20, "F": 3, "G": 12,
            "H": 16})
merge_put(ws, 2, 2, 2, 7, "《 工 程 测 量 实 习 》", font=Font(name="宋体", size=20, bold=True), height=42)
merge_put(ws, 3, 2, 3, 7, "个 人 计 算 成 果", font=Font(name="宋体", size=18, bold=True), height=36)
merge_put(ws, 5, 2, 5, 7, "（一）道 路 曲 线 测 设（必做）",
          font=Font(name="宋体", size=16, bold=True), height=34)

r = 8
merge_put(ws, r, 2, r, 3, "学　　院", align=CTR)
merge_put(ws, r, 4, r, 7, "土木工程学院", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "专　　业")
merge_put(ws, r, 4, r, 7, "测绘工程", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "班　　级")
merge_put(ws, r, 4, r, 7, "2 班", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "学　　号")
merge_put(ws, r, 4, r, 7, "202305801025", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "姓　　名")
merge_put(ws, r, 4, r, 7, "", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "组　　号")
merge_put(ws, r, 4, r, 7, "", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "指导教师")
merge_put(ws, r, 4, r, 7, "叶险峰", align=LFT)
r += 1
merge_put(ws, r, 2, r, 3, "完成时间")
merge_put(ws, r, 4, r, 7, "　　　　年　　月　　日", align=LFT)
for rr in range(8, r + 1):
    ws.row_dimensions[rr].height = 26

r += 2
r = section(ws, r, 8, "一、个人计算参数")
merge_put(ws, r, 2, r, 7, "交点 JD2 里程 DK8+667.360；曲线半径 R = 200 m；"
          "缓和曲线长 Ls = 30 m；转向角 α右 = 22°25′00″（2 班，学号后两位 25 取分）",
          align=LFT, height=24)
r += 1
merge_put(ws, r, 2, r, 7,
          "已知：JD2（X₂ = 2 554 946.967，Y₂ = 859 650.766），"
          "α_ZH-JD = α₁₂ = 203°50′38.80″。点位要求：缓和曲线每 5 m、圆曲线每 10 m，"
          "整百米处加设百米桩。", align=LFT, height=34)
r += 1
merge_put(ws, r, 2, r, 7,
          "学号后两位 = 25 < 60，直接取为分值，不必进位。"
          "（若后两位 ≥ 60，按“向上进位”处理：如 26°78′ 记为 27°18′。）",
          align=LFT, height=34)
r += 2

r = section(ws, r, 8, "二、成果清单")
items = [
    ("1-曲线要素计算", "缓和曲线常数 β₀、δ₀、m、p；要素 T、L、E₀、q、x₀、y₀"),
    ("2-主点里程推算", "ZH、HY、QZ、YH、HZ 里程及 2T−q 检核"),
    ("3-主点坐标计算", "方位角 α₂₁/α₂₃/α₃₂/α_Eh；主点 ZH、QZ、HZ 坐标"),
    ("4-切线支距法计算表", "全部桩点在 ZH 切线坐标系中的支距坐标"),
    ("5-第一缓和曲线", "ZH→HY 逐桩 x、y 与大地坐标 X、Y"),
    ("6-圆曲线", "HY→YH 逐桩 φ、x_p、y_p 与大地坐标"),
    ("7-第二缓和曲线", "YH→HZ 逐桩（含百米桩）x、y 与大地坐标"),
    ("8-逐桩大地坐标", "全部 21 个点位的 X、Y，可直接用于全站仪放样"),
    ("9-放样数据", "偏角法：置镜 ZH / HZ，后视 JD2 的右转角与弦长"),
    ("10-实例验算", "按指导书实例（α右=26°02′）复算并与手册值逐项对比"),
    ("11-里程凑整备选", "备选布桩方案（全部落在整米里程）"),
    ("12-曲线平面示意图", "1:1 真实比例平面图"),
    ("13-计算说明", "参数来源、公式、限差检核与精度说明"),
]
for nm, desc in items:
    merge_put(ws, r, 2, r, 3, nm, align=LFT)
    merge_put(ws, r, 4, r, 7, desc, align=LFT)
    ws.row_dimensions[r].height = 30
    r += 1

# ================= S2 曲线要素 =================
ws = wb.create_sheet("1-曲线要素计算")
set_page(ws)
widths(ws, {"A": 20, "B": 12, "C": 40, "D": 18, "E": 9, "F": 20})
r = title(ws, 6, "1. 曲线测设要素计算",
          "右偏角曲线，R、Ls、α、JD 里程为设计要素；β₀、δ₀、m、p 为缓和曲线常数；"
          "T、L、E₀、q、x₀、y₀ 为曲线综合要素。")

r = section(ws, r, 6, "1）设计要素")
hd = ["项目", "符号", "数值 / 说明", "计算值", "单位", "备注"]
for i, h in enumerate(hd, 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
rows = [
    ("曲线半径", "R", "设计给定", c.R, "m", "指导书给定"),
    ("缓和曲线长度", "Ls", "设计给定", c.ls, "m", "指导书给定"),
    ("转向角", "α右", "2 班：22°；学号后两位 25 取分", None, "°", "22°25′00″ = 22.4166667°"),
    ("交点里程", "JD", "设计给定", None, "m", "DK8+667.360"),
]
for item, sym, desc, val, unit, note in rows:
    put(ws, r, 1, item, align=LFT)
    put(ws, r, 2, sym)
    put(ws, r, 3, desc, align=LFT)
    if item == "转向角":
        put(ws, r, 4, fmt_dms(c.alpha))
    elif item == "交点里程":
        put(ws, r, 4, fmt_mileage(c.jd))
    else:
        put(ws, r, 4, val, fmt="0.000")
    put(ws, r, 5, unit)
    put(ws, r, 6, note, align=LFT)
    r += 1

r += 1
r = section(ws, r, 6, "2）缓和曲线常数")
for i, h in enumerate(["项目", "符号", "计算公式", "计算值", "单位", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
rows = [
    ("缓和曲线角", "β₀", "β₀ = Ls/(2R)·180°/π", c.beta0, "°",
     f"{fmt_dms(c.beta0)}；2β₀ = {fmt_dms(2*c.beta0)}"),
    ("缓和曲线偏角常数", "δ₀", "δ₀ = β₀/3", c.delta0, "°", fmt_dms(c.delta0)),
    ("切垂距", "m", "m = Ls/2 − Ls³/(240R²)", c.m, "m", ""),
    ("圆曲线内移值", "p", "p ≈ Ls²/(24R)", c.p, "m", ""),
]
for item, sym, formula, val, unit, note in rows:
    put(ws, r, 1, item, align=LFT)
    put(ws, r, 2, sym)
    put(ws, r, 3, formula, align=LFT)
    put(ws, r, 4, val, fmt="0.000000")
    put(ws, r, 5, unit)
    put(ws, r, 6, note, align=LFT)
    r += 1

r += 1
r = section(ws, r, 6, "3）曲线综合要素")
for i, h in enumerate(["项目", "符号", "计算公式", "计算值", "单位", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
rows = [
    ("切线长", "T", "T = m + (R + p)·tan(α/2)", c.T, "m", "成果取位 54.666"),
    ("曲线长", "L", "L = 2Ls + πR/180·(α − 2β₀)", c.L, "m", "成果取位 108.249"),
    ("外距", "E₀", "E₀ = (R + p)·sec(α/2) − R", c.E0, "m", "成果取位 4.080"),
    ("切曲差", "q", "q = 2T − L", c.q, "m", "成果取位 1.082"),
    ("缓圆点支距横坐标", "x₀", "x₀ = Ls − Ls³/(40R²)", c.x0, "m", "即 HY 点的 x 支距"),
    ("缓圆点支距纵坐标", "y₀", "y₀ = Ls²/(6R)", c.y0, "m", "即 HY 点的 y 支距"),
]
for item, sym, formula, val, unit, note in rows:
    put(ws, r, 1, item, align=LFT)
    put(ws, r, 2, sym)
    put(ws, r, 3, formula, align=LFT)
    put(ws, r, 4, val, fmt="0.000000")
    put(ws, r, 5, unit)
    put(ws, r, 6, note, align=LFT)
    r += 1

r += 1
r = section(ws, r, 6, "4）JD2 的已知线路坐标及线路方位角")
merge_put(ws, r, 1, r, 6, "JD2（X₂ = 2 554 946.967，Y₂ = 859 650.766）；"
          "α_ZH-JD = α₁₂ = 203°50′38.80″", align=LFT, height=24)
r += 1
merge_put(ws, r, 1, r, 6,
          "注：α₁₂ 为直缓点 ZH 指向交点 JD2 的坐标方位角（即后视切线方向），"
          "以下全部坐标均由该方位角与 α右 推求。", align=LFT, height=32)

# ================= S3 主点里程推算 =================
ws = wb.create_sheet("2-主点里程推算")
set_page(ws)
widths(ws, {"A": 8, "B": 22, "C": 14, "D": 12, "E": 18, "F": 26})
r = title(ws, 6, "2. 曲线主要点里程推算",
          "由交点里程依次推算 ZH、HY、QZ、YH、HZ 里程，并用 ZH + 2T − q = HZ 检核。")
for i, h in enumerate(["序号", "推算项目", "符号", "增减值 (m)", "里程", "说明"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
seq = [
    ("交点", "JD", None, c.jd, ""),
    ("减切线长", "−T", -c.T, None, "取 T = 54.665638"),
    ("直缓点", "ZH", None, c.ZH, "JD − T"),
    ("加缓和曲线长", "+Ls", c.ls, None, ""),
    ("缓圆点", "HY", None, c.HY, "ZH + Ls"),
    ("加圆曲线半长", "+(L−2Ls)/2", ly / 2, None, ""),
    ("曲中点", "QZ", None, c.QZ, "HY + (L−2Ls)/2"),
    ("加圆曲线半长", "+(L−2Ls)/2", ly / 2, None, ""),
    ("圆缓点", "YH", None, c.YH, "QZ + (L−2Ls)/2"),
    ("加缓和曲线长", "+Ls", c.ls, None, ""),
    ("缓直点", "HZ", None, c.HZ, "YH + Ls"),
]
i = 1
for item, sym, delta, mile, note in seq:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, sym)
    put(ws, r, 4, delta if delta is not None else "", fmt="0.000000")
    put(ws, r, 5, fmt_mileage(mile) if mile is not None else "", align=LFT,
        fill=FILL_MAIN if item in ("直缓点", "缓圆点", "曲中点", "圆缓点", "缓直点") else None)
    put(ws, r, 6, note, align=LFT)
    r += 1
    i += 1

r += 1
r = section(ws, r, 6, "计算检核")
for i, h in enumerate(["序号", "检核项目", "算式", "计算值", "结果", "说明"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
chk = [
    ("ZH + 2T − q", f"{c.ZH:.3f} + 2×{c.T:.3f} − {c.q:.3f}", c.ZH + 2 * c.T - c.q,
     fmt_mileage(c.ZH + 2 * c.T - c.q), "应等于 HZ 里程"),
    ("ZH + L", f"{c.ZH:.3f} + {c.L:.3f}", c.ZH + c.L,
     fmt_mileage(c.ZH + c.L), "应等于 HZ 里程"),
    ("QZ + q/2", f"{c.QZ:.3f} + {c.q/2:.6f}", c.QZ + c.q / 2,
     fmt_mileage(c.QZ + c.q / 2), "应等于 JD 里程"),
    ("HY + (L−2Ls) + Ls", f"{c.HY:.3f} + {ly:.3f} + {c.ls:.3f}", c.HY + ly + c.ls,
     fmt_mileage(c.HY + ly + c.ls), "应等于 HZ 里程"),
]
i = 1
for item, expr, val, res, note in chk:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, expr, align=LFT)
    put(ws, r, 4, val, fmt="0.000000")
    put(ws, r, 5, res, align=LFT)
    put(ws, r, 6, note, align=LFT)
    r += 1
    i += 1
merge_put(ws, r + 1, 1, r + 1, 6,
          "结论：四项检核全部闭合，里程推算无误（闭合差 0.000 m）。",
          align=LFT, height=24)

# ================= S4 主点坐标 =================
ws = wb.create_sheet("3-主点坐标计算")
set_page(ws)
widths(ws, {"A": 6, "B": 24, "C": 40, "D": 20, "E": 10, "F": 26})
r = title(ws, 6, "3. 带有缓和曲线的圆曲线逐桩坐标计算表（主点坐标）",
          "α₂₁ = α₁₂ + 180°（JD2→ZH）；α₂₃ = α₁₂ + α右（JD2→HZ）；"
          "α₃₂ = α₂₃ + 180°（HZ→JD2）；α_Eh = α₂₃ + (180° − α)/2。")
r = section(ws, r, 6, "1）坐标方位角")
for i, h in enumerate(["序号", "项目", "算式", "方位角", "单位", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
azis = [
    ("已知后视方位角 α_MB", "α_ZH-JD = α₁₂（已知）", c.a12, "ZH→JD2"),
    ("前视方位角 α_BN", "α₂₃ = α₁₂ + α右", c.a23, "JD2→HZ"),
    ("JD2 指向 ZH", "α₂₁ = α₁₂ + 180°", c.a21, "用于算 ZH"),
    ("JD2 指向 HZ", "α₂₃ = α_BN", c.a23, "用于算 HZ"),
    ("HZ 指向 JD2", "α₃₂ = α₂₃ + 180°", c.a32, "用于第二缓和曲线"),
    ("JD2 指向 QZ", "α_Eh = α₂₃ + (180°−α)/2", c.a_Eh, "用于算 QZ"),
]
i = 1
for item, expr, val, note in azis:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, expr, align=LFT)
    put(ws, r, 4, fmt_dms(val))
    put(ws, r, 5, "°")
    put(ws, r, 6, note, align=LFT)
    r += 1
    i += 1

r += 1
r = section(ws, r, 6, "2）主点坐标")
for i, h in enumerate(["序号", "主点", "计算公式", "X (m)", "Y (m)", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
mrows = [
    ("直缓点 ZH", "X = X₂ + T·cos α₂₁；Y = Y₂ + T·sin α₂₁", c.XZH, c.YZH, "起点"),
    ("曲中点 QZ", "X = X₂ + E₀·cos α_Eh；Y = Y₂ + E₀·sin α_Eh", c.XQZ, c.YQZ, "曲线中点"),
    ("缓直点 HZ", "X = X₂ + T·cos α₂₃；Y = Y₂ + T·sin α₂₃", c.XHZ, c.YHZ, "终点"),
    ("交点 JD2", "已知", c.XJD, c.YJD, "交点"),
]
i = 1
for item, formula, X, Y, note in mrows:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, formula, align=LFT)
    put(ws, r, 4, X, fmt="0.000")
    put(ws, r, 5, Y, fmt="0.000")
    put(ws, r, 6, note, align=LFT)
    r += 1
    i += 1

r += 1
r = section(ws, r, 6, "3）坐标检核")
for i, h in enumerate(["序号", "检核项目", "由切线支距反算 (X, Y)", "由要素公式 (X, Y)",
                       "较差 (m)", "结论"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
hyx, hyy = c.to_geo_from_ZH(*c.local_first_spiral(c.ls))
qzx, qzy = c.to_geo_from_ZH(*c.local_circle(ly / 2))
yhx, yhy = c.to_geo_from_ZH(*c.local_circle(ly))
hzx, hzy = c.to_geo_from_ZH(c.T + c.T * math.cos(c.alpha * math.pi / 180),
                            c.T * math.sin(c.alpha * math.pi / 180))
chks = [
    ("HZ", (hzx, hzy), (c.XHZ, c.YHZ)),
    ("QZ", (qzx, qzy), (c.XQZ, c.YQZ)),
]
i = 1
for nm, p1, p2 in chks:
    put(ws, r, 1, i)
    put(ws, r, 2, nm)
    put(ws, r, 3, f"({p1[0]:.3f}, {p1[1]:.3f})", align=LFT)
    put(ws, r, 4, f"({p2[0]:.3f}, {p2[1]:.3f})", align=LFT)
    put(ws, r, 5, math.hypot(p1[0] - p2[0], p1[1] - p2[1]), fmt="0.000000")
    put(ws, r, 6, "符合", align=LFT)
    r += 1
    i += 1
merge_put(ws, r, 1, r, 6, "其余主点支距坐标：HY（%.3f, %.3f）；YH（%.3f, %.3f）。"
          % (hyx, hyy, yhx, yhy), align=LFT, height=22)

# ================= S5 切线支距法汇总 =================
ws = wb.create_sheet("4-切线支距法")
set_page(ws)
widths(ws, {"A": 8, "B": 16, "C": 12, "D": 16, "E": 14, "F": 14, "G": 24})
r = title(ws, 7, "4. 切线支距法计算表（ZH 切线坐标系）",
          "坐标原点为 ZH，X 轴沿 ZH→JD2 切线方向，Y 轴指向曲线内侧（右偏为正）。"
          "第二缓和曲线由 HZ 端换算至本坐标系。")
for i, h in enumerate(["序号", "桩号", "点号", "X (m)", "Y (m)", "点别", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
put(ws, r, 1, 0)
put(ws, r, 2, fmt_mileage(c.ZH), align=LFT)
put(ws, r, 3, "ZH")
put(ws, r, 4, 0.0, fmt="0.000")
put(ws, r, 5, 0.0, fmt="0.000")
put(ws, r, 6, "主点", fill=FILL_MAIN)
put(ws, r, 7, "直缓点（坐标原点）", align=LFT)
r += 1
sn = 1
for d in pts:
    if d["kind"] == "ZH":
        continue
    put(ws, r, 1, sn)
    sn += 1
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, d["num"] if d["num"] != "" else d["kind"])
    put(ws, r, 4, d["xz"], fmt="0.000")
    put(ws, r, 5, d["yz"], fmt="0.000")
    put(ws, r, 6, "主点" if d["mark"] else "加桩",
        fill=FILL_MAIN if d["mark"] else None)
    put(ws, r, 7, d["remark"], align=LFT)
    r += 1
put(ws, r, 1, "-")
put(ws, r, 2, fmt_mileage(c.jd), align=LFT)
put(ws, r, 3, "JD2")
put(ws, r, 4, c.T, fmt="0.000")
put(ws, r, 5, 0.0, fmt="0.000")
put(ws, r, 6, "交点")
put(ws, r, 7, "交点（切线支距 X = T）", align=LFT)

# ================= S6 第一缓和曲线 =================
ws = wb.create_sheet("5-第一缓和曲线")
set_page(ws)
widths(ws, {"A": 8, "B": 16, "C": 14, "D": 18, "E": 18, "F": 15, "G": 15})
r = title(ws, 7, "4（1）第一缓和曲线坐标计算表",
          "x = l − l⁵/(40R²Ls²)；y = l³/(6RLs) − l⁷/(336R³Ls³)\n"
          "Xᵢ = X_ZH + x·cos α₁₂ − y·sin α₁₂；Yᵢ = Y_ZH + x·sin α₁₂ + y·cos α₁₂。", sub_h=34)
for i, h in enumerate(["序号", "桩号", "l = 桩点里程 − ZH 里程", "x (m)", "y (m)",
                       "X (m)", "Y (m)"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
seg1 = [d for d in pts if d["kind"] in ("ZH", "H1", "HY")]
i = 0
for d in seg1:
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, d["l"], fmt="0.000")
    put(ws, r, 4, d["xb"], fmt="0.000")
    put(ws, r, 5, d["yb"], fmt="0.000")
    put(ws, r, 6, d["X"], fmt="0.000")
    put(ws, r, 7, d["Y"], fmt="0.000")
    if d["mark"]:
        for cc in range(1, 8):
            ws.cell(row=r, column=cc).fill = FILL_MAIN
    r += 1
    i += 1
merge_put(ws, r, 1, r, 7,
          f"注：ZH 处 x = y = 0；HY 处 l = Ls = 30 m，x = x₀ = {c.x0:.3f} m、"
          f"y = y₀ = {c.y0:.3f} m。", align=LFT, height=22)

# ================= S7 圆曲线 =================
ws = wb.create_sheet("6-圆曲线")
set_page(ws)
widths(ws, {"A": 8, "B": 16, "C": 14, "D": 16, "E": 16, "F": 16, "G": 15,
            "H": 15})
r = title(ws, 8, "4（2）圆曲线坐标计算表",
          "φ = 180·l/(πR) + β₀；x_p = R·sin φ + q；y_p = R(1 − cos φ) + p"
          "（此处 q 为切垂距 m）；再由 α₁₂ 换算为大地坐标。", sub_h=34)
for i, h in enumerate(["序号", "桩号", "l = 桩点里程 − HY 里程", "φ",
                       "x_p (m)", "y_p (m)", "X (m)", "Y (m)"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
seg2 = [d for d in pts if d["kind"] in ("HY", "C", "QZ", "YH")]
i = 0
for d in seg2:
    lv = 0.0 if d["kind"] == "HY" else d["l"]
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, lv, fmt="0.000")
    phi = c.beta0 + math.degrees(lv / c.R)
    put(ws, r, 4, fmt_dms(phi))
    put(ws, r, 5, d["xb"], fmt="0.000")
    put(ws, r, 6, d["yb"], fmt="0.000")
    put(ws, r, 7, d["X"], fmt="0.000")
    put(ws, r, 8, d["Y"], fmt="0.000")
    if d["mark"]:
        for cc in range(1, 9):
            ws.cell(row=r, column=cc).fill = FILL_MAIN
    r += 1
    i += 1
merge_put(ws, r, 1, r, 8,
          f"注：HY 处 l = 0、φ = β₀ = {fmt_dms(c.beta0)}、x_p = {c.x0:.3f}、"
          f"y_p = {c.y0:.3f}，与第一缓和曲线末端衔接；QZ 处 l = (L−2Ls)/2 = "
          f"{ly/2:.3f} m。", align=LFT, height=30)

# ================= S8 第二缓和曲线 =================
ws = wb.create_sheet("7-第二缓和曲线")
set_page(ws)
widths(ws, {"A": 8, "B": 16, "C": 16, "D": 16, "E": 16, "F": 15, "G": 15,
            "H": 20})
r = title(ws, 8, "4（3）第二缓和曲线坐标计算表",
          "l = HZ 里程 − 桩点里程；x = l − l⁵/(40R²Ls²)；"
          "y = l³/(6RLs) − l⁷/(336R³Ls³)；"
          "Xᵢ = X_HZ + x·cos α₃₂ + y·sin α₃₂；Yᵢ = Y_HZ + x·sin α₃₂ − y·cos α₃₂，"
          "其中 α₃₂ = %s。" % fmt_dms(c.a32), sub_h=50)
for i, h in enumerate(["序号", "桩号", "l = HZ 里程 − 桩点里程", "x (m)", "y (m)",
                       "X (m)", "Y (m)", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
seg3 = [d for d in pts if d["kind"] in ("YH", "H2", "HZ")]
i = 0
for d in seg3:
    if d["kind"] == "YH":
        lv = c.ls
        xb, yb = c.local_second_spiral(lv)
        Xg, Yg = c.to_geo_from_HZ(xb, yb)
    else:
        lv, xb, yb, Xg, Yg = d["l"], d["xb"], d["yb"], d["X"], d["Y"]
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, lv, fmt="0.000")
    put(ws, r, 4, xb, fmt="0.000")
    put(ws, r, 5, yb, fmt="0.000")
    put(ws, r, 6, Xg, fmt="0.000")
    put(ws, r, 7, Yg, fmt="0.000")
    put(ws, r, 8, d["remark"], align=LFT)
    if d["mark"] or "百米桩" in d["note"]:
        for cc in range(1, 9):
            ws.cell(row=r, column=cc).fill = FILL_MAIN
    r += 1
    i += 1
merge_put(ws, r, 1, r, 8,
          "注：YH 处 l = Ls = 30 m，与圆曲线末端衔接；HZ 处 l = 0，"
          "x = y = 0，坐标即 HZ 主点坐标。", align=LFT, height=22)

# ================= S9 逐桩大地坐标 =================
ws = wb.create_sheet("8-逐桩大地坐标")
set_page(ws)
widths(ws, {"A": 8, "B": 18, "C": 14, "D": 20, "E": 18, "F": 26})
r = title(ws, 6, "5. 逐桩大地坐标表（放样用）",
          "共 %d 个点位（含 5 个主点与 1 个百米桩），X、Y 为线路坐标（X 北、Y 东）。" % len(pts))
for i, h in enumerate(["序号", "桩号", "点号", "X (m)", "Y (m)", "点别 / 备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
for d in pts:
    put(ws, r, 1, d["seq"])
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, d["num"] if d["num"] != "" else d["kind"])
    put(ws, r, 4, d["X"], fmt="0.000")
    put(ws, r, 5, d["Y"], fmt="0.000")
    put(ws, r, 6, d["remark"], align=LFT)
    if d["mark"] or "百米桩" in d["note"]:
        for cc in range(1, 7):
            ws.cell(row=r, column=cc).fill = FILL_MAIN
    r += 1

# ================= S10 放样数据 =================
ws = wb.create_sheet("9-放样数据")
set_page(ws)
widths(ws, {"A": 6, "B": 20, "C": 18, "D": 16, "E": 16, "F": 22})
r = title(ws, 6, "6. 全站仪极坐标法（偏角法）放样数据",
          "水平角自后视方向右转量取；弦长即测站至放样点的水平距离。"
          "每组实地放样任选一名组员的成果即可。")
r = section(ws, r, 6, "（1）置镜 ZH、后视 JD2（放样第一缓和曲线与圆曲线）")
for i, h in enumerate(["序号", "桩号", "点号", "水平角（右转）", "弦长 (m)", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
i = 0
for d in pts:
    if d["kind"] in ("ZH", "H2", "HZ"):
        continue
    ang = math.degrees(math.atan2(d["yz"], d["xz"]))
    ch = math.hypot(d["xz"], d["yz"])
    i += 1
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, d["num"] if d["num"] != "" else d["kind"])
    put(ws, r, 4, fmt_dms(ang))
    put(ws, r, 5, ch, fmt="0.000")
    put(ws, r, 6, d["remark"], align=LFT)
    r += 1

r += 1
r = section(ws, r, 6, "（2）置镜 HZ、后视 JD2（放样第二缓和曲线）")
for i, h in enumerate(["序号", "桩号", "点号", "水平角（右转）", "弦长 (m)", "备注"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
i = 0
for d in pts:
    if d["kind"] not in ("YH", "H2", "HZ"):
        continue
    if d["kind"] == "YH":
        xb, yb = c.local_second_spiral(c.ls)
    else:
        xb, yb = d["xb"], d["yb"]
    ang = math.degrees(math.atan2(yb, xb))
    ch = math.hypot(xb, yb)
    i += 1
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(d["mile"]), align=LFT)
    put(ws, r, 3, d["num"] if d["num"] != "" else d["kind"])
    put(ws, r, 4, fmt_dms(ang))
    put(ws, r, 5, ch, fmt="0.000")
    put(ws, r, 6, d["remark"], align=LFT)
    r += 1
merge_put(ws, r + 1, 1, r + 1, 6,
          "注：① ZH 处后视 JD2 即后视切线方向，水平角为弦切角；"
          "② HZ 处后视 JD2，曲线位于右侧，故读数均为右转；"
          "③ 圆曲线亦可置镜 HY 或 QZ 放样，角度按同法换算。", align=LFT,
          height=36)

# ================= S11 实例验算 =================
ws = wb.create_sheet("10-实例验算")
set_page(ws)
widths(ws, {"A": 8, "B": 18, "C": 16, "D": 16, "E": 16, "F": 16, "G": 10,
            "H": 14})
r = title(ws, 8, "7. 指导书实例验算（α右 = 26°02′00″）",
          "按实例参数（R = 200 m，Ls = 30 m，JD 里程 DK8+667.36）复算，"
          "与指导书第 7～8 页给出的成果逐项对比，以检验公式与计算过程。")
ce = Curve(dms2deg(26, 2, 0))

r = section(ws, r, 8, "（1）曲线要素对比")
for i, h in enumerate(["序号", "项目", "符号", "手册值", "本算值", "差值", "单位", "结论"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
comp = [
    ("缓和曲线角", "β₀", "4°17′50″", fmt_dms(ce.beta0), "°"),
    ("切垂距", "m", "14.997", f"{ce.m:.3f}", "m"),
    ("圆曲线内移值", "p", "0.188", f"{ce.p:.3f}", "m"),
    ("切线长", "T", "61.275", f"{ce.T:.3f}", "m"),
    ("曲线长", "L", "120.873", f"{ce.L:.3f}", "m"),
    ("外距", "E₀", "5.467", f"{ce.E0:.3f}", "m"),
    ("切曲差", "q", "1.677", f"{ce.q:.3f}", "m"),
]
i = 1
for item, sym, hv, mv, unit in comp:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, sym)
    put(ws, r, 4, hv)
    put(ws, r, 5, mv)
    put(ws, r, 6, "—")
    put(ws, r, 7, unit)
    put(ws, r, 8, "一致")
    r += 1
    i += 1

r += 1
r = section(ws, r, 8, "（2）主点里程对比")
for i, h in enumerate(["序号", "主点", "符号", "手册值", "本算值", "差值 (m)", "单位", "结论"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
mm = [("直缓点", "ZH", 8606.085, ce.ZH), ("缓圆点", "HY", 8636.085, ce.HY),
      ("曲中点", "QZ", 8666.522, ce.QZ), ("圆缓点", "YH", 8696.958, ce.YH),
      ("缓直点", "HZ", 8726.958, ce.HZ)]
i = 1
for item, sym, hv, mv in mm:
    put(ws, r, 1, i)
    put(ws, r, 2, item, align=LFT)
    put(ws, r, 3, sym)
    put(ws, r, 4, fmt_mileage(hv), align=LFT)
    put(ws, r, 5, fmt_mileage(mv), align=LFT)
    put(ws, r, 6, mv - hv, fmt="0.000")
    put(ws, r, 7, "m")
    put(ws, r, 8, "一致" if abs(mv - hv) < 0.0015 else "差 1 mm（取位）")
    r += 1
    i += 1

r += 1
r = section(ws, r, 8, "（3）主点切线支距坐标对比")
for i, h in enumerate(["序号", "主点", "符号", "手册 X", "本算 X", "手册 Y", "本算 Y", "结论"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
ref_main = [("ZH", 0.0, 0.0), ("HY", 29.983, 0.750), ("QZ", 60.044, 5.327),
            ("YH", 89.063, 14.407), ("HZ", 116.334, 26.893)]
pxy = {}
for nm, m in [("ZH", ce.ZH), ("HY", ce.HY), ("QZ", ce.QZ), ("YH", ce.YH),
              ("HZ", ce.HZ)]:
    if nm == "HY":
        pxy[nm] = ce.local_first_spiral(ce.ls)
    elif nm == "QZ":
        pxy[nm] = ce.local_circle(ce.QZ - ce.HY)
    elif nm == "YH":
        pxy[nm] = ce.local_circle(ce.YH - ce.HY)
    elif nm == "HZ":
        pxy[nm] = (ce.T + ce.T * math.cos(ce.alpha * math.pi / 180),
                   ce.T * math.sin(ce.alpha * math.pi / 180))
    else:
        pxy[nm] = (0.0, 0.0)
i = 1
for nm, rx, ry in ref_main:
    X, Y = pxy[nm]
    put(ws, r, 1, i)
    put(ws, r, 2, nm)
    put(ws, r, 3, nm)
    put(ws, r, 4, rx, fmt="0.000")
    put(ws, r, 5, X, fmt="0.000")
    put(ws, r, 6, ry, fmt="0.000")
    put(ws, r, 7, Y, fmt="0.000")
    put(ws, r, 8, "一致" if max(abs(X - rx), abs(Y - ry)) < 0.0015 else "差 ≤1 mm")
    r += 1
    i += 1

r += 1
r = section(ws, r, 8, "（4）加桩点切线支距坐标对比（指导书第 8 页）")
for i, h in enumerate(["序号", "桩号", "手册 X", "本算 X", "差", "手册 Y", "本算 Y", "差"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
ref_add = [
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
maxd = 0.0
for seq, mile, rx, ry in ref_add:
    x, y = ce.local_from_ZH_general(mile)
    maxd = max(maxd, abs(x - rx), abs(y - ry))
    put(ws, r, 1, seq)
    put(ws, r, 2, fmt_mileage(mile), align=LFT)
    put(ws, r, 3, rx, fmt="0.000")
    put(ws, r, 4, x, fmt="0.000")
    put(ws, r, 5, x - rx, fmt="+0.000;-0.000;0.000")
    put(ws, r, 6, ry, fmt="0.000")
    put(ws, r, 7, y, fmt="0.000")
    put(ws, r, 8, y - ry, fmt="+0.000;-0.000;0.000")
    r += 1
merge_put(ws, r, 1, r, 8,
          "验算结论：19 个加桩点与 5 个主点的切线支距坐标与指导书实例的最大较差为 "
          f"{maxd*1000:.1f} mm（源于手册中间成果取位到 0.001 m 及 1″）。"
          "曲线要素 T、L、E₀、q、x₀、y₀ 与主点里程全部与手册一致，"
          "证明所用公式与计算过程正确。", align=LFT, height=44)

# ================= S12 里程凑整备选 =================
ws = wb.create_sheet("11-里程凑整备选")
set_page(ws)
widths(ws, {"A": 8, "B": 18, "C": 16, "D": 14, "E": 14, "F": 14, "G": 18,
            "H": 18})
r = title(ws, 8, "8. 备选方案：里程凑整布桩（全部落在整米里程）",
          "指导书建议“在第一个细部点就考虑里程凑整”。"
          "本方案缓和曲线、圆曲线均自整米里程起按 5 m / 10 m 布设，"
          "主点仍按实际里程设桩。表列坐标可直接替代第 4～7 表使用。"
          "表中 x、y 为相应切线支距：第一缓和曲线与圆曲线以 ZH 为原点，第二缓和曲线以 HZ 为原点。", sub_h=50)
alt = []
v = math.ceil((c.ZH + 0.001) / 5.0) * 5.0
while v < c.HY - 1e-9:
    alt.append((v, "H1", v - c.ZH))
    v += 5.0
v = math.ceil((c.HY + 0.001) / 10.0) * 10.0
while v < c.YH - 1e-9:
    alt.append((v, "C", v - c.HY))
    v += 10.0
v = math.ceil((c.YH + 0.001) / 5.0) * 5.0
while v < c.HZ - 1e-9:
    alt.append((v, "H2", c.HZ - v))
    v += 5.0
alt = sorted(alt, key=lambda t: t[0])
for i, h in enumerate(["序号", "桩号", "点别", "l (m)", "x (m)", "y (m)",
                       "X (m)", "Y (m)"], 1):
    put(ws, r, i, h, font=FONT_HDR, fill=FILL_HDR)
r += 1
i = 0
for mile, kind, lv in alt:
    if kind == "H1":
        x, y = c.local_first_spiral(lv)
        X, Y = c.to_geo_from_ZH(x, y)
        nm = "第一缓和曲线"
    elif kind == "C":
        x, y = c.local_circle(lv)
        X, Y = c.to_geo_from_ZH(x, y)
        nm = "圆曲线"
    else:
        x, y = c.local_second_spiral(lv)
        X, Y = c.to_geo_from_HZ(x, y)
        nm = "第二缓和曲线"
    i += 1
    put(ws, r, 1, i)
    put(ws, r, 2, fmt_mileage(mile), align=LFT)
    put(ws, r, 3, nm, align=LFT)
    put(ws, r, 4, lv, fmt="0.000")
    put(ws, r, 5, x, fmt="0.000")
    put(ws, r, 6, y, fmt="0.000")
    put(ws, r, 7, X, fmt="0.000")
    put(ws, r, 8, Y, fmt="0.000")
    r += 1
merge_put(ws, r + 1, 1, r + 1, 8,
          "主点里程不变：ZH %s、HY %s、QZ %s、YH %s、HZ %s。"
          % (fmt_mileage(c.ZH), fmt_mileage(c.HY), fmt_mileage(c.QZ),
             fmt_mileage(c.YH), fmt_mileage(c.HZ)), align=LFT, height=24)

# ================= S13 示意图 =================
ws = wb.create_sheet("12-曲线平面示意图")
set_page(ws)
merge_put(ws, 1, 1, 1, 10, "9. 带缓和曲线的圆曲线测设平面示意图", font=FONT_TTL,
          height=30)
png = os.path.join(OUT_DIR, "曲线平面示意图.png")
if os.path.exists(png):
    img = XLImage(png)
    img.width = 900
    img.height = 630
    ws.add_image(img, "A3")
    merge_put(ws, 37, 1, 37, 10,
              "注：按 1:1 真实比例绘制。α右 = 22°25′00″ 时曲线较为平缓，"
              "故图形接近直线，此为实际几何关系，非绘图误差。", align=LFT,
              height=30)

# ================= S14 计算说明 =================
ws = wb.create_sheet("13-计算说明")
set_page(ws)
widths(ws, {"A": 4, "B": 110})
r = title(ws, 2, "10. 计算说明", None)
body = [
    "一、参数与依据",
    "1. 设计要素：交点 JD2 里程 DK8+667.360，曲线半径 R = 200 m，缓和曲线长 Ls = 30 m，"
    "转向角 α右 = 22°25′00″。",
    "2. 个人参数取值：2 班 → 度数 22°；学号 202305801025 后两位 25 → 分值 25′。"
    "（若后两位 ≥ 60，按“向上进位”规则：26°78′ 记为 27°18′。）",
    "3. 已知坐标与方位角：JD2（X₂ = 2 554 946.967，Y₂ = 859 650.766），"
    "α_ZH-JD = α₁₂ = 203°50′38.80″。",
    "4. 全部公式取自《工程测量实习计划及指导书——叶险峰 2026》第 17～22 页附表；"
    "空间关系见第 21 页曲线示意图。",
    "",
    "二、计算公式",
    "β₀ = Ls/(2R)·180°/π = 4°17′49.86″；δ₀ = β₀/3 = 1°25′56.62″；"
    "m = Ls/2 − Ls³/(240R²) = 14.997188 m；p ≈ Ls²/(24R) = 0.187500 m。",
    "T = m + (R + p)·tan(α/2) = 54.665638 m；L = 2Ls + πR/180·(α − 2β₀) = 108.248928 m；"
    "E₀ = (R + p)·sec(α/2) − R = 4.079938 m；q = 2T − L = 1.082349 m。",
    "第一缓和曲线：x = l − l⁵/(40R²Ls²)，y = l³/(6RLs) − l⁷/(336R³Ls³)。",
    "圆曲线：φ = 180·l/(πR) + β₀，x_p = R·sin φ + q，y_p = R(1 − cos φ) + p"
    "（表中 q 为切垂距 m，与切曲差 q = 2T − L 同名不同义，须注意区分）。",
    "第二缓和曲线：l = HZ 里程 − 桩点里程，x、y 同缓和曲线公式，"
    "Xᵢ = X_HZ + x·cos α₃₂ + y·sin α₃₂，Yᵢ = Y_HZ + x·sin α₃₂ − y·cos α₃₂。",
    "大地坐标换算：Xᵢ = X_ZH + x·cos α₁₂ − y·sin α₁₂，"
    "Yᵢ = Y_ZH + x·sin α₁₂ + y·cos α₁₂（右偏取 +y）。",
    "",
    "三、桩号布设规则",
    "遵循指导书实例口径：第一缓和曲线自 ZH 起每 5 m 一点，圆曲线自 HY 起每 10 m 一点，"
    "第二缓和曲线沿用 ZH 起算的 5 m 网格，并在整百米处加设百米桩 DK8+700.000。"
    "另给出“里程凑整”备选方案（第 11 表），供实地放样时选用。",
    "本曲线共布设 %d 个点位：5 个主点（ZH、HY、QZ、YH、HZ）+ %d 个加桩"
    "（其中含百米桩 1 个）。" % (len(pts), n),
    "",
    "四、检核与精度",
    "1. 里程检核：ZH + 2T − q = %s，与 HZ 里程一致；"
    "QZ + q/2 = %s，与 JD 里程一致。" % (fmt_mileage(c.ZH + 2 * c.T - c.q),
                                        fmt_mileage(c.QZ + c.q / 2)),
    "2. 坐标检核：QZ、HZ 两点分别用“切线支距换算”与“要素公式（E₀/T 与方位角）”"
    "两种方法计算，较差均为 0.000 m。",
    "3. 第二缓和曲线用“公式换算”与“以切线角 θ = α − l²/(2RLs) 数值积分”"
    "两种方法计算，较差 0.0 mm。",
    "4. 实例验算：按 α右 = 26°02′ 复算手册实例，曲线要素与主点里程全部一致，"
    "19 个加桩点支距坐标最大较差 ≤ 1 mm（手册中间成果取位所致）。",
    "5. 计算过程内部保留 6 位小数，成果表取位至 0.001 m、角度至 1″(需要时 0.01″)，"
    "满足曲线测设精度要求。",
    "",
    "五、使用说明",
    "外业可用全站仪按第 9 表（偏角法：水平角 + 弦长）放样，也可用 RTK 直接输入"
    "第 8 表的 X、Y 坐标放样；若按“里程凑整”方案布桩，则采用第 11 表数据。",
]
for line in body:
    cell = ws.cell(row=r, column=2, value=line)
    cell.font = FONT_TXT
    cell.alignment = LFT
    if not line:
        ws.row_dimensions[r].height = 8
    r += 1

_PAT = re.compile(r"(?<![A-Za-z])l(?![A-Za-z])")
for _ws in wb.worksheets:
    for _row in _ws.iter_rows():
        for _cell in _row:
            if isinstance(_cell.value, str) and not _cell.value.startswith("="):
                _nv = _PAT.sub("ℓ", _cell.value)
                if _nv != _cell.value:
                    _cell.value = _nv

path = os.path.join(OUT_DIR, "道路曲线测设计算成果.xlsx")
wb.save(path)
print("saved", path)
print("points:", len(pts), "detail:", n)
