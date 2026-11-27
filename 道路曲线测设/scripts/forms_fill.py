# -*- coding: utf-8 -*-
"""
把《工程测量实习》指导书中的曲线测设空白表格页(手册第17~21页 / PDF第18~22页)
原样取出，填入个人成果(2班 202305801025, alpha右=22d25m00s)，生成填写版 PDF。
"""
import math
import os
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from curve_core import Curve, dms2deg, fmt_dms, fmt_mileage   # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

SRC = r"C:\Users\31710\OneDrive\Desktop\测量数据\要求\工程测量实习计划及指导书-叶险峰2026.pdf"
OUT_DIR = r"C:\Users\31710\OneDrive\Desktop\测量数据\道路曲线测设"
FONT = r"C:\Windows\Fonts\simsun.ttc"
INK = (0.03, 0.10, 0.45)
BLACK = (0, 0, 0)

c = Curve(dms2deg(22, 25, 0))
ly = c.L - 2 * c.ls
F = pymupdf.Font(fontfile=FONT)


def fit_size(text, maxw, pref, minsz=6.0):
    s = pref
    while s > minsz and F.text_length(text, fontsize=s) > maxw:
        s -= 0.2
    return round(s, 1)


def put(page, x, ybase, text, size=10.0, align="left", color=INK):
    w = F.text_length(text, fontsize=size)
    if align == "center":
        x -= w / 2
    elif align == "right":
        x -= w
    page.insert_text((x, ybase), text, fontname="song", fontsize=size,
                     color=color)
    return w


def put_cell(page, x0, x1, y_center, text, size=9.0, color=INK, dy=3.1,
             pad=3.0):
    s = fit_size(text, (x1 - x0) - 2 * pad, size)
    put(page, (x0 + x1) / 2, y_center + dy, text, size=s, align="center",
        color=color)
    return s


def num(v, nd=3):
    return f"{v:.{nd}f}"


station = fmt_mileage

# ---------------- 加桩编排 ----------------
h1 = []
l = 5.0
while l < c.ls - 1e-9:
    h1.append(c.ZH + l)
    l += 5.0
cir = []
l = 10.0
while l < ly - 1e-9:
    cir.append(c.HY + l)
    l += 10.0
h2 = []
k = 1
while True:
    v = c.ZH + 5.0 * k
    if v >= c.HZ - 1e-9:
        break
    if v > c.YH + 1e-9:
        h2.append(v)
    k += 1
kk = int(c.ZH // 100) + 1
while kk * 100.0 < c.HZ - 1e-9:
    v = kk * 100.0
    if v > c.YH + 1e-9:
        h2.append(v)
    kk += 1
h2 = sorted(h2)


def sp1(m):
    x, y = c.local_first_spiral(m - c.ZH)
    X, Y = c.to_geo_from_ZH(x, y)
    return m - c.ZH, x, y, X, Y


def circ(m):
    lc = m - c.HY
    x, y = c.local_circle(lc)
    X, Y = c.to_geo_from_ZH(x, y)
    return lc, c.beta0 + math.degrees(lc / c.R), x, y, X, Y


def sp2(m):
    lp = c.HZ - m
    x, y = c.local_second_spiral(lp)
    X, Y = c.to_geo_from_HZ(x, y)
    return lp, x, y, X, Y


src = pymupdf.open(SRC)
out = pymupdf.open()


def new_page():
    p = out.new_page(width=595.3, height=841.9)
    p.insert_font(fontname="song", fontfile=FONT)
    return p


def hb_page(pno):
    out.insert_pdf(src, from_page=pno, to_page=pno)
    p = out[-1]
    p.insert_font(fontname="song", fontfile=FONT)
    return p


# ============================ 封面 ============================
pg = new_page()
pg.draw_rect(pymupdf.Rect(56, 66, 539, 296), color=BLACK, width=1.2)
put(pg, 297.6, 128, "《 工 程 测 量 实 习 》", size=22, align="center",
    color=BLACK)
put(pg, 297.6, 170, "道路曲线测设（必做）", size=17, align="center",
    color=BLACK)
put(pg, 297.6, 206, "指 导 书 表 格 填 写 成 果", size=17, align="center",
    color=BLACK)
put(pg, 297.6, 246, "（按指导书第 17～21 页原表填写）", size=11,
    align="center", color=BLACK)
put(pg, 297.6, 274, "二〇二六年十一月", size=11, align="center", color=BLACK)

rows = [("学　　院", "土木工程学院"), ("专　　业", "测绘工程"),
        ("班　　级", "2 班"), ("学　　号", "202305801025"),
        ("姓　　名", ""), ("组　　号", ""), ("指导教师", "叶险峰")]
y = 302
RH = 24
pg.draw_rect(pymupdf.Rect(140, y, 460, y + RH * len(rows)), color=BLACK,
             width=0.8)
for i, (k, v) in enumerate(rows):
    yy = y + RH * i
    if i:
        pg.draw_line((140, yy), (460, yy), color=BLACK, width=0.8)
    pg.draw_line((215, yy), (215, yy + RH), color=BLACK, width=0.8)
    put(pg, 177, yy + 16, k, size=10.5, align="center", color=BLACK)
    put(pg, 225, yy + 16, v, size=10.5, color=BLACK)

yy = 486
put(pg, 84, yy, "一、个人计算参数", size=11, color=BLACK)
yy += 18
lines = [
    "交点 JD2 里程 DK8+667.360；曲线半径 R = 200 m；缓和曲线长 Ls = 30 m；",
    "转向角 α右 = 22°25′00″（2 班，学号后两位 25 取分，小于 60 无需进位）",
    "已知 JD2：X2 = 2554946.967，Y2 = 859650.766；已知方位角",
    "α12（ZH→JD）= 203°50′38.80″",
    "缓和曲线常数：β0 = 4°17′49.86″，δ0 = 1°25′56.62″，",
    "　　　　　　　m = 14.997188 m，p = 0.187500 m，",
    "　　　　　　　x0 = 29.983125 m，y0 = 0.750000 m",
    "曲线综合要素：T = 54.665638 m，L = 108.248928 m，",
    "　　　　　　　E0 = 4.079938 m，q = 1.082349 m",
    "主点里程：ZH DK8+612.694，HY DK8+642.694，QZ DK8+666.819，",
    "　　　　　　YH DK8+690.943，HZ DK8+720.943",
]
for t in lines:
    put(pg, 84, yy, t, size=9.2, color=BLACK)
    yy += 14.2

yy += 8
put(pg, 84, yy, "二、桩号布设说明", size=11, color=BLACK)
yy += 18
lines = [
    "1. 第一缓和曲线自 ZH 起每 5 m 一点（5 点）；圆曲线自 HY 起每 10 m 一点（4 点）；",
    "2. 第二缓和曲线沿用 ZH 起算的 5 m 网格（6 点），整百米处加设百米桩 DK8+700.000；",
    f"3. 全曲线共 {5 + len(h1) + len(cir) + len(h2)} 个点位（5 个主点 + "
    f"{len(h1) + len(cir) + len(h2)} 个加桩）；",
    "4. 第二缓和曲线加桩 7 个、超出原表 5 个，第 5 页按原表格式增加 2 行（行高压缩），",
    "　 其余各表均为指导书原表；各表坐标均由 α12 与 α右 推求，第二缓和曲线按 HZ 端",
    "　 α32 = 46°15′38.80″ 换算。",
]
for t in lines:
    put(pg, 84, yy, t, size=9.2, color=BLACK)
    yy += 14.2

yy += 8
put(pg, 84, yy, "三、计算与校核结论", size=11, color=BLACK)
yy += 18
for t in [
    "· 里程检核：ZH + 2T - q = DK8+720.943，与 HZ 里程一致；",
    "· 坐标检核：QZ、HZ 分别由切线支距反算与要素公式计算，较差 0.000 m；",
    "· 指导书实例（α右 = 26°02′）复算，曲线要素与主点里程全部一致，19 个加桩点",
    "　支距坐标最大较差 ≤ 1 mm。",
]:
    put(pg, 84, yy, t, size=9.2, color=BLACK)
    yy += 14.2

# ==================== 第1表 曲线测设要素计算 (PDF 18) ====================
pg = hb_page(17)
SZ = 10.5
put(pg, 130.5, 138.6, "200", size=SZ)
put(pg, 302.5, 138.6, "30", size=SZ)
put(pg, 428.0, 138.6, "22°25′00″（右）", size=9.2)
put(pg, 205.0, 162.1, "8", size=SZ, align="center")
put(pg, 229.0, 162.1, "667.360", size=SZ)
put(pg, 195.5, 215.5, fmt_dms(c.beta0), size=SZ)
put(pg, 166.5, 253.9, fmt_dms(c.delta0), size=SZ)
put(pg, 198.0, 294.9, num(c.m, 6) + " m", size=SZ)
put(pg, 162.5, 336.2, num(c.p, 6) + " m", size=SZ)
put(pg, 230.5, 398.3, num(c.T, 6) + " m", size=SZ)
put(pg, 298.5, 436.2, num(c.L, 6) + " m", size=SZ)
put(pg, 225.0, 474.3, num(c.E0, 6) + " m", size=SZ)
put(pg, 171.0, 504.7, num(c.q, 6) + " m", size=SZ)
put(pg, 190.0, 537.7, num(c.x0, 6) + " m", size=SZ)
put(pg, 161.0, 571.5, num(c.y0, 6) + " m", size=SZ)

# ==================== 第2表 主点里程推算 (PDF 19) ====================
pg = hb_page(18)
T1_ROWS = [169.84, 193.44, 217.04, 240.64, 264.24, 287.84, 311.44, 335.04,
           358.64, 382.24, 405.84]
T1_VALS = [(c.jd, 1), (c.T, 0), (c.ZH, 1), (c.ls, 0), (c.HY, 1),
           (ly / 2, 0), (c.QZ, 1), (ly / 2, 0), (c.YH, 1), (c.ls, 0),
           (c.HZ, 1)]
for yc, (val, is_m) in zip(T1_ROWS, T1_VALS):
    if is_m:
        put(pg, 226.0, yc + 7.6, station(val)[2:], size=13)
    else:
        put(pg, 210.0, yc + 7.6, f"{val:.3f}", size=13)

T2 = [(500.7, c.ZH, 1), (533.5, 2 * c.T, 0), (557.3, c.ZH + 2 * c.T, 1),
      (586.4, c.q, 0), (620.9, c.HZ, 1)]
for ybase, val, is_m in T2:
    if is_m:
        put(pg, 248.0, ybase, station(val)[2:], size=11.5)
    else:
        put(pg, 233.0, ybase, f"{val:.3f}", size=11.5)

# ============ 第3表 逐桩坐标计算表(主点坐标) (PDF 20) ============
pg = hb_page(19)
R20 = [117.32, 145.07, 172.82, 200.57, 228.32, 256.07, 283.82, 311.57,
       339.32, 367.07, 394.82, 422.57, 450.32, 478.07, 505.82, 533.57,
       561.32, 589.07, 616.82, 644.57, 672.32, 700.07, 727.82]
V20 = [fmt_dms(c.a12), fmt_dms(c.a23), fmt_dms(c.alpha, 0), fmt_dms(c.beta0),
       num(c.p, 4), num(c.m, 3), num(c.T, 6), num(c.L, 6), num(c.E0, 6),
       num(c.q, 6), station(c.ZH), station(c.HY), station(c.YH),
       station(c.HZ), station(c.QZ), station(c.jd), num(c.XZH), num(c.YZH),
       num(c.XHZ), num(c.YHZ), fmt_dms(c.a_Eh), num(c.XQZ), num(c.YQZ)]
for yc, v in zip(R20, V20):
    put(pg, 405.0, yc + 3.6, v, size=9.5)

# ============ 第4表 细部点坐标计算表 (PDF 21) ============
pg = hb_page(20)
# (1) 第一缓和曲线: 桩号列已印点号, 只填 l/x/y/Xi/Yi
C1 = [(129.00, 207.40), (207.40, 282.55), (282.55, 386.95), (386.95, 450.95),
      (450.95, 515.65)]
R1 = [250.22, 278.87, 307.51, 336.16, 364.82, 393.47, 422.12]
rows1 = [c.ZH] + h1 + [c.HY]
for yc, m in zip(R1, rows1):
    lv, x, y, X, Y = sp1(m)
    for (x0, x1), v, sz in zip(C1, [num(lv), num(x), num(y), num(X), num(Y)],
                               [9.0, 9.0, 9.0, 8.4, 8.4]):
        put_cell(pg, x0, x1, yc, v, size=sz)

# (2) 圆曲线: 表头上方 β0 / p / q
put(pg, 116.5, 480.3, "4°17′50″", size=7.0)
put(pg, 192.0, 480.6, num(c.p, 4), size=10)
put(pg, 276.0, 480.6, num(c.m, 3), size=10)

C2 = [(114.05, 186.75), (186.75, 268.00), (268.00, 346.15), (346.15, 426.05),
      (426.05, 469.50), (469.50, 515.65)]
R2 = [581.99, 613.26, 640.84, 668.44, 696.01, 723.59, 751.19]
rows2 = [c.HY] + cir[:2] + [c.QZ] + cir[2:] + [c.YH]
for yc, m in zip(R2, rows2):
    lc, phi, x, y, X, Y = circ(m)
    vals = [num(lc), fmt_dms(phi), num(x), num(y), num(X), num(Y)]
    for (x0, x1), v, sz in zip(C2, vals, [9.0, 9.0, 9.0, 9.0, 7.6, 7.6]):
        put_cell(pg, x0, x1, yc, v, size=sz)

# ============ 第5表 第二缓和曲线 (PDF 22) — 数据行重排为 9 行 ============
pg = hb_page(21)
COLS = [79.65, 128.95, 207.25, 282.40, 397.05, 462.35, 515.65]
TOP, BOT = 197.89, 420.84
NR = 1 + len(h2) + 1
H = (BOT - TOP) / NR
pg.draw_rect(pymupdf.Rect(79.3, TOP + 0.2, 516.0, BOT - 0.2), color=None,
             fill=(1, 1, 1), width=0)
for i in range(NR + 1):
    y = TOP + H * i
    pg.draw_line((COLS[0], y), (COLS[-1], y), color=BLACK, width=0.8)
for x in COLS:
    pg.draw_line((x, TOP), (x, BOT), color=BLACK, width=0.8)
pg.draw_rect(pymupdf.Rect(COLS[0], TOP, COLS[-1], BOT), color=BLACK, width=0.9)

put(pg, 163.0, 108.1, fmt_dms(c.a32), size=10)

labels = ["YH"] + [str(10 + i) for i in range(len(h2))] + ["HZ"]
rows5 = [c.YH] + h2 + [c.HZ]
cw = list(zip(COLS[:-1], COLS[1:]))
for i, (lab, m) in enumerate(zip(labels, rows5)):
    yc = TOP + H * (i + 0.5)
    put_cell(pg, cw[0][0], cw[0][1], yc, lab, size=9.0)
    lp, x, y, X, Y = sp2(m)
    vals = [num(lp), num(x), num(y), num(X), num(Y)]
    for (x0, x1), v, sz in zip(cw[1:], vals, [9.0, 9.0, 9.0, 8.0, 8.0]):
        put_cell(pg, x0, x1, yc, v, size=sz)
    if abs(m % 100.0) < 1e-9 and m > c.ZH:
        put(pg, (cw[0][0] + cw[0][1]) / 2, yc - 3.4, "百米桩", size=5.8,
            align="center")

try:
    out.subset_fonts()
except Exception as _e:
    print("subset_fonts skipped:", _e)
out.set_metadata({"title": "道路曲线测设 指导书表格填写成果",
                  "author": "2班 202305801025"})
path = os.path.join(OUT_DIR, "道路曲线测设（指导书表格填写版）.pdf")
out.save(path, garbage=4, deflate=True)
print("saved:", path, "pages:", out.page_count)
