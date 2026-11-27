# -*- coding: utf-8 -*-
"""
道路曲线测设 计算内核
带缓和曲线的圆曲线（右偏角）
按《工程测量实习计划及指导书-叶险峰2026》第 17-22 页公式链
"""
import math

D2R = math.pi / 180.0


# ---------------- 角度工具 ----------------
def dms2deg(d, m, s=0.0):
    return d + m / 60.0 + s / 3600.0


def deg2dms(x):
    """返回 (d, m, s) 秒保留 2 位"""
    x = x % 360.0
    d = int(x)
    rest = (x - d) * 60.0
    m = int(rest)
    s = (rest - m) * 60.0
    s = round(s, 2)
    if s >= 60.0:
        s -= 60.0
        m += 1
    if m >= 60:
        m -= 60
        d += 1
    return d, m, s


def fmt_dms(x, sec_fmt=2):
    d, m, s = deg2dms(x)
    if sec_fmt == 0:
        s = round(s)
        if s >= 60:
            s = 0.0
            m += 1
        if m >= 60:
            m = 0
            d += 1
        return f"{d:d}°{m:02d}′{int(s):02d}″"
    return f"{d:d}°{m:02d}′{s:0{3+sec_fmt}.{sec_fmt}f}″"


def fmt_mileage(v):
    """里程 DK8+667.360"""
    km = int(v // 1000)
    rest = v - km * 1000
    return f"DK{km}+{rest:07.3f}"


# ---------------- 曲线模型 ----------------
class Curve:
    def __init__(self, alpha_right_deg, R=200.0, ls=30.0, jd_mileage=8667.36,
                 JD_X=2554946.967, JD_Y=859650.766, a12_deg=None):
        self.alpha = alpha_right_deg          # 偏角(度)
        self.R = R
        self.ls = ls
        self.jd = jd_mileage
        self.JDX = JD_X
        self.JDY = JD_Y
        # 已知方位角 alpha_ZH-JD = alpha12
        self.a12 = a12_deg if a12_deg is not None else dms2deg(203, 50, 38.8)

        a = self.alpha * D2R
        # --- 缓和曲线常数 ---
        self.beta0 = math.degrees(ls / (2 * R))          # 缓和曲线角
        self.delta0 = self.beta0 / 3.0                    # 缓和曲线偏角常数
        self.m = ls / 2 - ls ** 3 / (240 * R ** 2)        # 切垂距
        self.p = ls ** 2 / (24 * R)                       # 圆曲线内移值
        # --- 曲线综合要素 ---
        self.T = self.m + (R + self.p) * math.tan(a / 2)
        self.L = 2 * ls + math.pi * R / 180.0 * (self.alpha - 2 * self.beta0)
        self.E0 = (R + self.p) / math.cos(a / 2) - R
        self.q = 2 * self.T - self.L
        self.x0 = ls - ls ** 3 / (40 * R ** 2)
        self.y0 = ls ** 2 / (6 * R)
        # --- 主点里程 ---
        self.ZH = self.jd - self.T
        self.HY = self.ZH + ls
        self.QZ = self.ZH + self.L / 2
        self.YH = self.ZH + self.L - ls
        self.HZ = self.ZH + self.L
        # --- 方位角 ---
        self.a21 = (self.a12 + 180.0) % 360.0            # JD2 -> ZH
        self.a23 = (self.a12 + self.alpha) % 360.0       # JD2 -> HZ (前切线)
        self.a32 = (self.a23 + 180.0) % 360.0            # HZ -> JD2
        self.a_Eh = (self.a23 + (180.0 - self.alpha) / 2) % 360.0
        # --- 主点坐标 ---
        self.XZH = JD_X + self.T * math.cos(self.a21 * D2R)
        self.YZH = JD_Y + self.T * math.sin(self.a21 * D2R)
        self.XHZ = JD_X + self.T * math.cos(self.a23 * D2R)
        self.YHZ = JD_Y + self.T * math.sin(self.a23 * D2R)
        self.XQZ = JD_X + self.E0 * math.cos(self.a_Eh * D2R)
        self.YQZ = JD_Y + self.E0 * math.sin(self.a_Eh * D2R)
        self.XJD, self.YJD = JD_X, JD_Y

    # ---- 切线支距(本地系, x 沿 ZH->JD, y 指向曲线内侧/右侧) ----
    def local_first_spiral(self, l):
        R, ls = self.R, self.ls
        x = l - l ** 5 / (40 * R ** 2 * ls ** 2)
        y = l ** 3 / (6 * R * ls) - l ** 7 / (336 * R ** 3 * ls ** 3)
        return x, y

    def local_circle(self, lc):
        """lc: 自 HY 起算的圆曲线长
        注意: 手册圆曲线公式中的 q 是"切线增长值"(=m), 不是切曲差 2T-L"""
        R, p, q = self.R, self.p, self.m
        phi = math.degrees(lc / R) + self.beta0
        x = R * math.sin(phi * D2R) + q
        y = R * (1 - math.cos(phi * D2R)) + p
        return x, y

    def local_second_spiral(self, lp):
        """lp: 自 HZ 起算(往 YH 方向)的缓和曲线长, 返回 HZ 切线支距
        x' 沿 HZ->JD 方向, y' 为曲线内侧"""
        R, ls = self.R, self.ls
        x = lp - lp ** 5 / (40 * R ** 2 * ls ** 2)
        y = lp ** 3 / (6 * R * ls) - lp ** 7 / (336 * R ** 3 * ls ** 3)
        return x, y

    # ---- 本地系(x,y) -> 大地坐标 ----
    def to_geo_from_ZH(self, x, y):
        c, s = math.cos(self.a12 * D2R), math.sin(self.a12 * D2R)
        return self.XZH + x * c - y * s, self.YZH + x * s + y * c

    def to_geo_from_HZ(self, x, y):
        """按手册 p22: X=X_HZ+x'cos(a32)+y'sin(a32); Y=Y_HZ+x'sin(a32)-y'cos(a32)"""
        c, s = math.cos(self.a32 * D2R), math.sin(self.a32 * D2R)
        return self.XHZ + x * c + y * s, self.YHZ + x * s - y * c

    def local_from_HZ_backward(self, lp):
        """用积分把 HZ 往后 lp 处的点化到 ZH 切线系(x 沿 ZH->JD)"""
        XHZ_t, YHZ_t = self.T + self.T * math.cos(self.alpha * D2R), \
                       self.T * math.sin(self.alpha * D2R)
        # 数值积分: 位置 = HZ - ∫_0^lp (cos θ, sin θ) dl, θ = α - l²/(2R ls)
        n, h = 200, lp / 200.0
        sx = sy = 0.0
        for i in range(n + 1):
            ll = i * h
            th = (self.alpha - math.degrees(ll ** 2 / (2 * self.R * self.ls))) * D2R
            w = 1 if i in (0, n) else (4 if i % 2 else 2)
            sx += w * math.cos(th)
            sy += w * math.sin(th)
        sx *= h / 3.0
        sy *= h / 3.0
        return XHZ_t - sx, YHZ_t - sy

    def local_from_ZH_general(self, mileage):
        """通用: 任意桩号的本地切线支距坐标 (以 ZH 切线系为准)"""
        if mileage <= self.HY + 1e-9:
            return self.local_first_spiral(mileage - self.ZH)
        if mileage <= self.YH + 1e-9:
            return self.local_circle(mileage - self.HY)
        return self.local_from_HZ_backward(self.HZ - mileage)

    # ---- 桩号编排 ----
    def station_plan(self):
        """按手册实例编排: 缓和曲线自 ZH 起每 5m, 圆曲线自 HY 起每 10m,
        第二缓和曲线沿用 ZH 起 5m 网格, 另加整百米桩"""
        st = []
        # 第一缓和曲线
        l = 5.0
        while l < self.ls - 1e-9:
            st.append(("HS1", self.ZH + l))
            l += 5.0
        # 圆曲线
        l = 10.0
        while l < (self.YH - self.HY) - 1e-9:
            st.append(("CIR", self.HY + l))
            l += 10.0
        st.append(("CIR", self.QZ))
        # 第二缓和曲线: ZH 起 5m 网格中 > YH 且 < HZ 的桩
        k = 1
        while True:
            v = self.ZH + 5.0 * k
            if v >= self.HZ - 1e-9:
                break
            if v > self.YH + 1e-9:
                st.append(("HS2", v))
            k += 1
        # 整百米桩
        km = math.floor(self.ZH / 100.0) + 1
        while km * 100.0 < self.HZ - 1e-9:
            v = km * 100.0
            if v > self.ZH + 1e-9 and v <= self.YH + 1e-9:
                st.append(("CIR", v))
            elif v > self.YH + 1e-9:
                st.append(("HS2", v))
            km += 1
        st.sort(key=lambda t: t[1])
        return st
