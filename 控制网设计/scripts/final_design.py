# -*- coding: utf-8 -*-
"""最终设计: QZ2 移到北岸桥头(660), 其余 6 点用优化结果
桥轴线 QZ1(南岸)-QZ2(北岸) 跨江, QZ3 在岸上引桥, 9 点全部在陆地
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
SCR = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\scripts"
NEW = {
    "QZ1": (0.0, 0.0), "QZ2": (660.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-208.4, 0.0), "QN2": (-339.1, 0.0),
    "BX": (820.0, -188.7), "BD": (820.0, 188.7),
    "NN": (-300.0, -162.2), "ND": (-300.0, 162.2)}
OLD = {
    "QZ1": (0.0, 0.0), "QZ2": (400.0, 0.0), "QZ3": (800.0, 0.0),
    "QN1": (-346.8, 0.0), "QN2": (-503.0, 0.0),
    "BX": (831.6, -294.2), "BD": (831.6, 294.2),
    "NN": (-429.6, -232.8), "ND": (-429.6, 232.8)}

for fn in ["cnet.py", "run_prec.py", "build_cnet.py"]:
    p = os.path.join(SCR, fn)
    s = io.open(p, encoding="utf-8").read()
    n = 0
    for k, v in OLD.items():
        a = f'"{k}": ({v[0]:.1f}, {v[1]:.1f})'
        b = f'"{k}": ({NEW[k][0]:.1f}, {NEW[k][1]:.1f})'
        if a in s:
            s = s.replace(a, b)
            n += 1
    io.open(p, "w", encoding="utf-8").write(s)
    print(f"{fn}: replaced {n}/9")
