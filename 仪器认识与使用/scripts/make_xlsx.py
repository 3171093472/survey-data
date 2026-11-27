# -*- coding: utf-8 -*-
"""面积测量计算 + CPⅢ 观测限差检核 工具(xlsx)"""
import os
import sys

from openpyxl import Workbook
from openpyxl.chart import ScatterChart, Reference, Series
from openpyxl.chart.marker import Marker
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\仪器认识与使用"
os.makedirs(OUT, exist_ok=True)

TH = Side(style="thin", color="000000")
BD = Border(left=TH, right=TH, top=TH, bottom=TH)
F10 = Font(name="宋体", size=10)
FB = Font(name="宋体", size=10, bold=True)
FTT = Font(name="宋体", size=13, bold=True)
FH = PatternFill("solid", fgColor="DCE6F1")
FIN = PatternFill("solid", fgColor="FFF2CC")     # 输入区(黄)
FRES = PatternFill("solid", fgColor="E8F5E9")    # 结果区(绿)
FRED = PatternFill("solid", fgColor="FFD6D6")
CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
LFT = Alignment(horizontal="left", vertical="center", wrap_text=True)


def c(ws, r, col, v, font=F10, align=CTR, fmt=None, fill=None, border=True):
    x = ws.cell(row=r, column=col, value=v)
    x.font = font
    x.alignment = align
    if border:
        x.border = BD
    if fmt:
        x.number_format = fmt
    if fill:
        x.fill = fill
    return x


wb = Workbook()

# ================= Sheet1 面积测量计算 =================
ws = wb.active
ws.title = "1-面积测量计算"
for col, w in zip("ABCDEFGHI", [6, 10, 14, 14, 12, 14, 14, 12, 12]):
    ws.column_dimensions[col].width = w
ws.merge_cells("A1:H1")
c(ws, 1, 1, "全站仪面积测量计算表（坐标解析法）", FTT, border=False)
ws.merge_cells("A2:H2")
c(ws, 2, 1, "填写黄色区域：点号、X（北）、Y（东）。最后一行必须重复输入第 1 点以闭合多边形。",
  Font(name="宋体", size=9), LFT, border=False, fill=FIN)
c(ws, 3, 8, "点数 n =", FB)
c(ws, 3, 9, "=COUNT(C5:C24)-1", FB, fmt="0", fill=FRES)
c(ws, 4, 2, "点位中误差 mP (mm) =", FB, border=False)
c(ws, 4, 3, 5, FB, fmt="0.0", fill=FIN)
hdr = ["序号", "点号", "X（北） m", "Y（东） m", "边长 m", "∂S/∂X", "∂S/∂Y", "", ""]
for j, h in enumerate(hdr[:7], 1):
    c(ws, 5, j, h, FB, fill=FH)
N = 20
for i in range(N):
    r = 6 + i
    c(ws, r, 1, i + 1, F10)
    c(ws, r, 2, None, F10, fill=FIN)
    c(ws, r, 3, None, F10, fmt="0.000", fill=FIN)
    c(ws, r, 4, None, F10, fmt="0.000", fill=FIN)
    # 边长(到下一点)
    c(ws, r, 5, f'=IF(AND(C{r}<>"",C{r+1}<>""),SQRT((C{r+1}-C{r})^2+(D{r+1}-D{r})^2),"")',
      F10, fmt="0.000")
    # 面积梯度: ∂S/∂Xi=(Yi+1-Yi-1)/2, ∂S/∂Yi=(Xi-1-Xi+1)/2
    idx = i + 1
    nxt = f"MOD({idx},$I$3)+1"
    prv = f"MOD({idx}-2+$I$3,$I$3)+1"
    nxt = f"MOD(ROW()-5,$I$3)+1"
    prv = f"MOD(ROW()-5-2+$I$3,$I$3)+1"
    guard = f'OR(C{r}="",$I$3=0,ROW()-5>$I$3)'
    c(ws, r, 6,
      f'=IF({guard},"",(INDEX($D$6:$D$25,{nxt})-INDEX($D$6:$D$25,{prv}))/2)',
      F10, fmt="0.000")
    c(ws, r, 7,
      f'=IF({guard},"",(INDEX($C$6:$C$25,{prv})-INDEX($C$6:$C$25,{nxt}))/2)',
      F10, fmt="0.000")

r0, r1 = 6, 6 + N - 1
c(ws, 4, 5, "面积 S =", FB)
c(ws, 4, 6, "=0.5*ABS(SUMPRODUCT(C6:C26,D7:D27)-SUMPRODUCT(D6:D26,C7:C27))",
  FB, fmt="0.000", fill=FRES)
c(ws, 4, 7, "m²", FB)
c(ws, 5, 5, "", F10)
ws.merge_cells("A28:H28")
c(ws, 28, 1, "计算结果", FB, fill=FH, align=LFT)
rows_res = [
    ("面积 S（m²）", "=0.5*ABS(SUMPRODUCT($C$6:$C$25,$D$7:$D$26)-SUMPRODUCT($D$6:$D$25,$C$7:$C$26))", "0.000"),
    ("面积 S（亩，1 亩=666.667 m²）",
     "=0.5*ABS(SUMPRODUCT($C$6:$C$25,$D$7:$D$26)-SUMPRODUCT($D$6:$D$25,$C$7:$C$26))/666.6667", "0.0000"),
    ("周长（m）", "=SUM(E6:E25)", "0.000"),
    ("面积中误差 mS（m²）",
     "=($C$4/1000)*SQRT(SUMPRODUCT(F6:F25,F6:F25)+SUMPRODUCT(G6:G25,G6:G25))", "0.000"),
    ("面积相对精度 1/…",
     "=0.5*ABS(SUMPRODUCT($C$6:$C$25,$D$7:$D$26)-SUMPRODUCT($D$6:$D$25,$C$7:$C$26))"
     "/(($C$4/1000)*SQRT(SUMPRODUCT(F6:F25,F6:F25)+SUMPRODUCT(G6:G25,G6:G25)))", "0"),
]
for i, (lab, fml, fmt) in enumerate(rows_res):
    r = 29 + i
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
    c(ws, r, 1, lab, FB, LFT)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    c(ws, r, 3, fml, FB, fmt=fmt, fill=FRES)

# 示意图散点图
ch = ScatterChart()
ch.title = "测点平面位置示意图"
ch.x_axis.title = "Y（东）/m"
ch.y_axis.title = "X（北）/m"
ch.style = 13
ch.height = 9
ch.width = 12
ch.x_axis.delete = False
ch.y_axis.delete = False
xref = Reference(ws, min_col=4, min_row=6, max_row=25)
yref = Reference(ws, min_col=3, min_row=6, max_row=25)
s = Series(yref, xref, title="测点")
s.marker = Marker(symbol="circle", size=7)
s.graphicalProperties.line.width = 15000
ch.series.append(s)
ws.add_chart(ch, "J6")

# ================= Sheet2 CPⅢ 观测记录与检核 =================
ws2 = wb.create_sheet("2-CPⅢ观测检核")
widths = [6, 8, 9, 6, 6, 6, 6, 8, 6, 12, 6, 6, 6, 6, 6, 6, 9, 9, 9, 10, 9, 9, 14]
for i, w in enumerate(widths, 1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.merge_cells("A1:R1")
c(ws2, 1, 1, "测量机器人 CPⅢ 平面网 自由设站观测记录与限差检核", FTT, border=False)
ws2.merge_cells("A2:R2")
c(ws2, 2, 1, "蓝底为填写区（角度按 度/分/秒 分三列输入；距离单位 m）。"
  "仪器等级 0.5″，测回数 2；限差：半测回归零差 6″，不同测回同一方向 2C 互差 9″，"
  "同一方向归零后方向值较差 6″，测回间竖盘指标差互差 ≤6″，竖直角互差 ≤6″，距离较差 ≤1 mm。",
  Font(name="宋体", size=9), LFT, border=False, fill=FIN)
# 表头(两级)
grp = [(1, 1, "测回"), (2, 2, "目标点"), (3, 5, "盘左方向 (° ′ ″)"),
       (6, 8, "盘右方向 (° ′ ″)"), (9, 9, "2C(″)"), (10, 10, "平均方向(°)"),
       (11, 13, "天顶距盘左"), (14, 16, "天顶距盘右"), (17, 17, "指标差(″)"),
       (18, 18, "斜距1(m)"), (19, 19, "斜距2(m)"), (20, 20, "较差(mm)")]
for a, b, t in grp:
    if a != b:
        ws2.merge_cells(start_row=3, start_column=a, end_row=3, end_column=b)
    c(ws2, 3, a, t, FB, fill=FH)
for j in range(1, 21):
    ws2.cell(row=3, column=j).border = BD
sub = ["", "", "°", "′", "″", "°", "′", "″", "", "", "°", "′", "″", "°", "′", "″",
       "", "", "", ""]
for j, t in enumerate(sub, 1):
    c(ws2, 4, j, t, FB, fill=FH)
NR = 2 * 4          # 2 测回 × (3 目标 + 归零)
for i in range(NR):
    r = 5 + i
    c(ws2, r, 1, (i // 4) + 1, F10)          # 测回
    c(ws2, r, 2, None, F10, fill=FIN)        # 目标点
    for j in range(3, 9):
        c(ws2, r, j, None, F10, fill=FIN)
    # 2C = 盘左 - 盘右 ± 180 (秒)
    c(ws2, r, 9, f'=IF(OR(C{r}="",F{r}=""),"",'
      f'ROUND(((C{r}+D{r}/60+E{r}/3600)-(F{r}+G{r}/60+H{r}/3600))*3600,1)'
      f'-IF(((C{r}+D{r}/60+E{r}/3600)-(F{r}+G{r}/60+H{r}/3600))>0,180*3600,-180*3600))',
      F10, fmt="0.0")
    Lc = f"(C{r}+D{r}/60+E{r}/3600)"
    Rc = f"(F{r}+G{r}/60+H{r}/3600)"
    c(ws2, r, 10, f'=IF(OR(C{r}="",F{r}=""),"",MOD(({Lc}+{Rc}'
      f'+IF({Rc}>180,-180,180))/2,360))', F10, fmt="0.000000")
    for j in range(11, 17):
        c(ws2, r, j, None, F10, fill=FIN)
    c(ws2, r, 17, f'=IF(OR(K{r}="",N{r}=""),"",'
      f'ROUND(((K{r}+L{r}/60+M{r}/3600)+(N{r}+O{r}/60+P{r}/3600)-360)*1800,1))',
      F10, fmt="0.0")
    c(ws2, r, 18, None, F10, fmt="0.0000", fill=FIN)
    c(ws2, r, 19, None, F10, fmt="0.0000", fill=FIN)
    c(ws2, r, 20, f'=IF(OR(R{r}="",S{r}=""),"",ROUND((R{r}-S{r})*1000,1))',
      F10, fmt="0.0")
    TS = f"ROUND(J{r}*3600,1)"
    c(ws2, r, 23, f'=IF(J{r}="","",TEXT(INT({TS}/3600),"0")&"°"&'
      f'TEXT(INT(MOD({TS},3600)/60),"00")&"′"&'
      f'TEXT(MOD({TS},60),"00.0")&"″")', F10)

# 检核汇总
r = 5 + NR + 1
ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=8)
c(ws2, r, 1, "限差检核汇总（自动计算，判定合格/超限）", FB, fill=FH, align=LFT)
# 归零后方向值(辅助列 U/V)
c(ws2, 4, 21, "归零后 U", FB, fill=FH)
c(ws2, 4, 22, "归零后 V", FB, fill=FH)
for k in range(3):
    r1 = 5 + k
    c(ws2, r1, 21, f'=IF(J{r1}="","",MOD(J{r1}-J$5,360)*3600)', F10, fmt="0.0")
    r2_ = 9 + k
    c(ws2, r2_, 22, f'=IF(J{r2_}="","",MOD(J{r2_}-J$9,360)*3600)', F10, fmt="0.0")
chk = [
    ("半测回归零差最大值（″）", '=MAX(ABS(MOD(J8-J5,360)*3600),ABS(MOD(J12-J9,360)*3600))', 6),
    ("不同测回同一方向 2C 互差（″）", '=MAX(I5:I12)-MIN(I5:I12)', 9),
    ("同一方向归零后方向值较差（″）",
     '=MAX(ABS(U5-V9),ABS(U6-V10),ABS(U7-V11))', 6),
    ("测回间竖盘指标差互差（″）", '=MAX(Q5:Q12)-MIN(Q5:Q12)', 6),
    ("测回间距离较差最大值（mm）", '=MAX(T5:T12)', 1),
]
for i, (lab, fml, lim) in enumerate(chk):
    rr = r + 1 + i
    ws2.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=6)
    c(ws2, rr, 1, lab, FB, LFT)
    c(ws2, rr, 7, fml, FB, fmt="0.0", fill=FRES)
    c(ws2, rr, 8, f"≤{lim}", F10)
    c(ws2, rr, 9, f'=IF(G{rr}="","",IF(ABS(G{rr})<={lim},"合格","超限"))', FB, fill=FRES)

# 限差表
r2 = r + 8
ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=8)
c(ws2, r2, 1, "CPⅢ 平面网 观测限差（按指导书）", FB, fill=FH, align=LFT)
lims = [("控制网名称", "仪器等级", "测回数", "半测回归零差", "不同测回同一方向 2C 互差",
         "同一方向归零后方向值较差"),
        ("CPⅢ 平面网", "0.5″", "2", "6″", "9″", "6″")]
for i, row in enumerate(lims):
    for j, v in enumerate(row, 1):
        c(ws2, r2 + 1 + i, j, v, FB if i == 0 else F10,
          fill=FH if i == 0 else None)
ws2.merge_cells(start_row=r2 + 3, start_column=1, end_row=r2 + 3, end_column=8)
c(ws2, r2 + 3, 1, "另：测回间竖盘指标差互差 ≤6″，测回间竖直角互差 ≤6″，"
  "测回间距离较差 ≤1 mm。", Font(name="宋体", size=9), LFT, border=False)

# ================= Sheet3 说明 =================
ws3 = wb.create_sheet("3-使用说明")
ws3.column_dimensions["A"].width = 4
ws3.column_dimensions["B"].width = 110
lines = [
    "一、面积测量计算表",
    "1. 在“1-面积测量计算”表黄色区域依次输入点号、X（北）、Y（东）；"
    "点序按顺时针或逆时针统一方向排列。",
    "2. 最后一行必须重复输入第 1 点，使多边形闭合（程序按闭合环计算）。",
    "3. 面积按坐标解析法（鞋带公式）S = 1/2·|Σ(Xi·Yi+1 − Xi+1·Yi)| 自动计算，"
    "同时给出周长、面积中误差与相对精度。",
    "4. 面积中误差 mS = mP·√(Σ(∂S/∂Xi)²+Σ(∂S/∂Yi)²)，"
    "其中 ∂S/∂Xi=(Yi+1−Yi−1)/2，∂S/∂Yi=(Xi−1−Xi+1)/2；"
    "mP 为点位中误差（mm），按全站仪标称精度与作业条件填 5～10 mm。",
    "5. 右侧自动生成测点平面位置示意图，可直接截取放入报告。",
    "",
    "二、CPⅢ 观测检核表",
    "1. 每个测站 2 个测回，每测回观测 3 个以上目标点，并归零（最后一行为归零方向）。",
    "2. 角度按 度、分、秒 分三列输入（如 12°34′56″ 输入 12 / 34 / 56）；"
    "天顶距同样处理；斜距单位 m。",
    "3. 程序自动计算 2C 值、各测回平均方向值、竖盘指标差、距离较差，"
    "并在下方“限差检核汇总”中与限差比较，给出合格/超限判定。",
    "4. 注意：I 列（2C）对归零行同样有效；若某方向超限，应说明原因并重测。",
    "",
    "三、填写到指导书的表格",
    "· 面积测量成果表（指导书第 26 页）：测点、坐标 X/Y、示意图、面积值；",
    "· 测量机器人的认识和使用（指导书第 27 页）：测量场地安排及观测站点略图、"
    "徕拓智能测量系统流程及设置、测量数据（图片）及质量评价。",
]
rr = 2
for t in lines:
    cell = ws3.cell(row=rr, column=2, value=t)
    cell.font = FB if (t and not t[0].isdigit() and t[0] != "·") else F10
    cell.alignment = LFT
    ws3.row_dimensions[rr].height = 30 if t else 8
    rr += 1

path = os.path.join(OUT, "面积测量与CPⅢ检核工具.xlsx")
wb.save(path)
print("saved", path)
