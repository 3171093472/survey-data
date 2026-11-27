# -*- coding: utf-8 -*-
"""修正封面桥位行超宽; Excel 增加桥位/影像说明"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\scripts\build_cnet.py"
s = io.open(p, encoding="utf-8").read()

old = '''    "桥位：在湘江湘潭段卫星影像（中心约 112.9655°E、27.9169°N）上选线，"
    "河宽约 715 m，800 m 桥跨两岸各约 40 m 引桥。",'''
new = '''    "桥位：在湘江湘潭段卫星影像（中心约 112.9655°E、27.9169°N）上选线，"
    "河宽约 715 m；",
    "800 m 桥跨两岸各约 40 m 引桥，QZ1、QZ3 位于两岸，QZ2 位于河中。",'''
assert old in s
s = s.replace(old, new)

# Excel: 坐标表下加说明
old2 = '''ws3 = wb.create_sheet("3-观测方案清单")'''
new2 = '''_r = 13
ws.merge_cells("A13:C13")
wcell(ws, 13, 1, "说明：本表为独立坐标系（原点 QZ1，X 轴沿桥轴线指向 QZ3）；"
      "桥位取自湘江湘潭段卫星影像（Esri World Imagery），"
      "中心约 112.9655°E、27.9169°N。", Font(name="宋体", size=9), LFT,
      border=False)

ws3 = wb.create_sheet("3-观测方案清单")'''
assert old2 in s
s = s.replace(old2, new2)
io.open(p, "w", encoding="utf-8").write(s)
print("patched")
