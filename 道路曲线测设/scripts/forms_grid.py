# -*- coding: utf-8 -*-
"""解析指导书空白表格页: 只保留长表格线(排除公式分数线), 输出精确网格"""
import sys
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\31710\OneDrive\Desktop\测量数据\要求\工程测量实习计划及指导书-叶险峰2026.pdf"
doc = pymupdf.open(SRC)


def grid(page, min_hlen=150, min_vlen=12):
    hs, vs = [], []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                if abs(p1.y - p2.y) < 0.6 and abs(p2.x - p1.x) >= min_hlen:
                    hs.append((p1.y, min(p1.x, p2.x), max(p1.x, p2.x)))
                elif abs(p1.x - p2.x) < 0.6 and abs(p2.y - p1.y) >= min_vlen:
                    vs.append((p1.x, min(p1.y, p2.y), max(p1.y, p2.y)))
            elif it[0] == "re":
                r = it[1]
                if r.width >= min_hlen:
                    hs += [(r.y0, r.x0, r.x1), (r.y1, r.x0, r.x1)]
                if r.height >= min_vlen:
                    vs += [(r.x0, r.y0, r.y1), (r.x1, r.y0, r.y1)]
    def cluster(items):
        out = []
        for it in sorted(items):
            v = it[0]
            if out and abs(v - out[-1][-1][0]) <= 1.2:
                out[-1].append(it)
            else:
                out.append([it])
        return [(sum(x[0] for x in g) / len(g),
                 min(x[1] for x in g), max(x[2] for x in g)) for g in out]
    return cluster(hs), cluster(vs)


for pno in (17, 18, 19, 20, 21):
    page = doc[pno]
    hs, vs = grid(page)
    print("=" * 76)
    print(f"PDF 第 {pno+1} 页 (手册第 {pno} 页)")
    print(f"  横线 y (共{len(hs)}):")
    for y, x0, x1 in hs:
        print(f"    y={y:7.2f}   x {x0:6.1f} -> {x1:6.1f}  长 {x1-x0:6.1f}")
    print(f"  竖线 x (共{len(vs)}):")
    for x, y0, y1 in vs:
        print(f"    x={x:7.2f}   y {y0:6.1f} -> {y1:6.1f}  长 {y1-y0:6.1f}")
    rows = [hs[i][0] for i in range(len(hs) - 1)
            if hs[i + 1][0] - hs[i][0] > 6]
    if rows:
        print(f"  行带(共{len(rows)}行):")
        for i in range(len(hs) - 1):
            a, b = hs[i][0], hs[i + 1][0]
            if b - a > 6:
                print(f"    row{i:02d}: {a:7.2f} -> {b:7.2f}  h={b-a:5.1f}"
                      f"  中线 {((a+b)/2):7.2f}")
