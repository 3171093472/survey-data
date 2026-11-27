# -*- coding: utf-8 -*-
"""QZ2 还原为 400 (设计不变), 并在 siteG 影像上重绘控制网图"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
SCR = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\scripts"
for fn in ["cnet.py", "run_prec.py", "build_cnet.py", "make_netfig_img.py"]:
    p = os.path.join(SCR, fn)
    s = io.open(p, encoding="utf-8").read()
    s2 = s.replace('"QZ2": (660.0, 0.0)', '"QZ2": (400.0, 0.0)')
    if s2 != s:
        io.open(p, "w", encoding="utf-8").write(s2)
        print("reverted", fn)
    else:
        print("no change", fn)
