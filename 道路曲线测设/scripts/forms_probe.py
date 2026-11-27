# -*- coding: utf-8 -*-
"""解析指导书空白表格页的版面: 表格线 -> 行带/列界, 以及文字基线"""
import sys
import pymupdf

sys.stdout.reconfigure(encoding="utf-8")
SRC = r"C:\Users\31710\OneDrive\Desktop\测量数据\要求\工程测量实习计划及指导书-叶险峰2026.pdf"
doc = pymupdf.open(SRC)


def lines(page):
    hs, vs = [], []
    for d in page.get_drawings():
        for it in d["items"]:
            if it[0] == "l":
                p1, p2 = it[1], it[2]
                if abs(p1.y - p2.y) < 0.6 and abs(p2.x - p1.x) > 8:
                    hs.append((round(p1.y, 1), round(min(p1.x, p2.x), 1),
                               round(max(p1.x, p2.x), 1)))
                elif abs(p1.x - p2.x) < 0.6 and abs(p2.y - p1.y) > 8:
                    vs.append((round(p1.x, 1), round(min(p1.y, p2.y), 1),
                               round(max(p1.y, p2.y), 1)))
            elif it[0] == "re":
                r = it[1]
                hs.append((round(r.y0, 1), round(r.x0, 1), round(r.x1, 1)))
                hs.append((round(r.y1, 1), round(r.x0, 1), round(r.x1, 1)))
                vs.append((round(r.x0, 1), round(r.y0, 1), round(r.y1, 1)))
                vs.append((round(r.x1, 1), round(r.y0, 1), round(r.y1, 1)))
    return hs, vs


def cluster(vals, tol=1.2):
    out = []
    for v in sorted(vals):
        if out and abs(v - out[-1][-1]) <= tol:
            out[-1].append(v)
        else:
            out.append([v])
    return [sum(g) / len(g) for g in out]


for pno in (17, 18, 19, 20, 21):
    page = doc[pno]
    print("=" * 78)
    print(f"PDF 第 {pno+1} 页  (手册第 {pno} 页)  size={page.rect}")
    hs, vs = lines(page)
    ys = cluster([h[0] for h in hs])
    xs = cluster([v[0] for v in vs])
    print(f"\n  水平线 y 坐标({len(ys)}): {[round(y,1) for y in ys]}")
    print(f"  垂直线 x 坐标({len(xs)}): {[round(x,1) for x in xs]}")
    # 表格行带
    bands = []
    for i in range(len(ys) - 1):
        if ys[i + 1] - ys[i] > 6:
            bands.append((ys[i], ys[i + 1]))
    print(f"\n  行带(相邻横线, 共{len(bands)}):")
    for i, (a, b) in enumerate(bands):
        print(f"    row{i:02d}: y {a:7.1f} -> {b:7.1f}  高 {b-a:6.1f}")
    print(f"\n  文字 span:")
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                t = sp["text"]
                if not t.strip():
                    continue
                x0, y0, x1, y1 = sp["bbox"]
                print(f"    ({x0:6.1f},{y0:6.1f})-({x1:6.1f},{y1:6.1f}) "
                      f"base={sp['origin'][1]:6.1f} sz={sp['size']:.1f} "
                      f"|{t}|")
