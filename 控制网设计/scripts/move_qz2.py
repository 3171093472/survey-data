# -*- coding: utf-8 -*-
"""把 QZ2 从河中(400)移到北岸桥头(660), 使 9 个控制点全部位于陆地
同时在各脚本中同步该坐标"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
SCR = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\scripts"
FILES = ["cnet.py", "run_prec.py", "build_cnet.py", "make_netfig_img.py"]
for fn in FILES:
    p = os.path.join(SCR, fn)
    if not os.path.exists(p):
        print("skip", fn)
        continue
    s = io.open(p, encoding="utf-8").read()
    before = s
    s = s.replace('"QZ2": (400.0, 0.0)', '"QZ2": (660.0, 0.0)')
    if s != before:
        io.open(p, "w", encoding="utf-8").write(s)
        print("patched", fn)
    else:
        print("no change", fn)
