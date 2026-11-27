# -*- coding: utf-8 -*-
"""把 build_cnet.py 中的控制网图替换为影像底图版本"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\scripts\build_cnet.py"
s = io.open(p, encoding="utf-8").read()
n = 0

old = '''p = hb(29)
fig = os.path.join(OUT, "控制网图.png")
if os.path.exists(fig):
    p.insert_image(pymupdf.Rect(88, 120, 508, 288), filename=fig)'''
new = '''p = hb(29)
fig = os.path.join(OUT, "控制网图（影像底图）.png")
if os.path.exists(fig):
    _h = 165.0
    _w = _h * 775.0 / 430.0
    _x0 = (595.3 - _w) / 2
    p.insert_image(pymupdf.Rect(_x0, 119, _x0 + _w, 119 + _h), filename=fig)'''
if old in s:
    s = s.replace(old, new)
    n += 1
else:
    print("WARN p29 fig")

old2 = '''# ---------- 附图页(横向): 控制网图放大 ----------
p2 = new_page(841.9, 595.3)
put(p2, 420.9, 52, "附图　控制网图（详图）", 14, "center", BLACK)
if os.path.exists(fig):
    p2.insert_image(pymupdf.Rect(60, 70, 800, 70 + 740 * 6.6 / 13.2),
                    filename=fig)'''
new2 = '''# ---------- 附图页(纵向): 三种方案影像底图对照 ----------
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
        BLACK)'''
if old2 in s:
    s = s.replace(old2, new2)
    n += 1
else:
    print("WARN f2 page")

old3 = '''    f"全网 9 点：桥轴线 QZ1、QZ2、QZ3；南引桥 QN1、QN2；北岸 BX、BD；南岸 NN、ND。",'''
new3 = '''    "桥位：在湘江湘潭段卫星影像（中心约 112.9655°E、27.9169°N）上选线，"
    "河宽约 715 m，800 m 桥跨两岸各约 40 m 引桥。",
    f"全网 9 点：桥轴线 QZ1、QZ2、QZ3；南引桥 QN1、QN2；北岸 BX、BD；南岸 NN、ND。",'''
if old3 in s:
    s = s.replace(old3, new3)
    n += 1
else:
    print("WARN cover")

old4 = '''    "本网为桥梁施工专用 GNSS 控制网，桥长 800 m，按大桥三等布设。9 点中 QZ1—QZ2—QZ3",'''
new4 = '''    "本网在湘江湘潭段卫星影像上选线布设：桥轴线横跨湘江（河宽约 715 m），"
    "QZ1、QZ3 分设两岸，QZ2 位于河中，",
    "桥长 800 m，按大桥三等布设。9 点中 QZ1—QZ2—QZ3",'''
if old4 in s:
    s = s.replace(old4, new4)
    n += 1
else:
    print("WARN analysis")

io.open(p, "w", encoding="utf-8").write(s)
print("patched", n)
