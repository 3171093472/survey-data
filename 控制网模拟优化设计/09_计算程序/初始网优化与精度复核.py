"""Select and check two successive COSA observation subsets without changing observations."""
from __future__ import annotations

import argparse
import csv
import itertools
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ARCSEC = math.pi / (180 * 3600)
PAIR = lambda a, b: tuple(sorted((a, b)))
SHORE = {"QZ2", "QZ3", "BX", "BD"}
LIMITS = np.array([0.004, 1 / 120000, 0.005, 1 / 300000])
SINGLE_DATUM_SECOND_STAGE_REMOVED_PAIRS = {
    ("ND", "QZ2"),
    ("BX", "QZ2"),
    ("QN1", "QZ3"),
    ("NN", "QN1"),
    ("QN1", "QN2"),
    ("BD", "QN2"),
    ("NN", "QZ2"),
}


def angle(token):
    deg, _, frac = token.strip().lstrip("+-").partition(".")
    frac = (frac + "000000")[:6]
    value = int(deg) + int(frac[:2]) / 60 + int(frac[2:]) / 360000
    return math.radians(-value if token.strip().startswith("-") else value)


def wrap(radians):
    return (radians + math.pi) % (2 * math.pi) - math.pi


@dataclass(frozen=True)
class Record:
    station: str
    target: str
    kind: str
    value: str
    line: str

    @property
    def key(self):
        if self.kind == "L":
            return ("L", self.station, self.target)
        return ("S", *PAIR(self.station, self.target))


class Network:
    def __init__(self, source, coordinates, azimuth_count):
        self.source = source
        self.xy = coordinates
        self.azimuth_count = azimuth_count
        self.points = tuple(coordinates)
        self.header = []
        self.stations = {}
        self.fixed = {}
        self.groups = {}
        for raw in source.read_text(encoding="ascii").splitlines():
            if not raw.strip():
                continue
            cols = [x.strip() for x in raw.split(",")]
            if len(cols) == 1:
                station = cols[0]
                self.stations[station] = []
            elif not self.stations:
                self.header.append(raw)
                if len(cols) == 3:
                    self.fixed[cols[0]] = np.array(cols[1:], dtype=float)
            else:
                rec = Record(station, *cols[:3], raw)
                self.stations[station].append(rec)
                if rec.kind in ("L", "S"):
                    self.groups.setdefault(rec.key, []).append(rec)
        precision = [float(x) for x in self.header[0].split(",")[:3]]
        assert precision == [1.8, 2, 2] and len(self.stations) == 9
        assert sorted(len(v) for k, v in self.groups.items() if k[0] == "S") == [2] * 35
        self.keys = tuple(self.groups)
        self.reference = {next(rec.key for rec in rows if rec.kind == "L")
                          for rows in self.stations.values()}
        self.pairs = tuple(itertools.combinations(self.points, 2))
        self.dist = np.array([np.linalg.norm(self.xy[b] - self.xy[a]) for a, b in self.pairs])
        self.longest = np.argmax(self.dist)
        self.columns = {}
        for k in self.points:
            for axis in range(2):
                if k not in self.fixed and not (azimuth_count and k == "QZ2" and axis == 1):
                    self.columns[k, axis] = len(self.columns)
        self.ori = {k: i for i, k in enumerate(self.stations, len(self.columns))}
        self.u = len(self.columns) + len(self.ori)
        self.pairs_rows = np.array([self.baseline_row(a, b, self.xy) for a, b in self.pairs])
        self.sets = {p: tuple(self.columns[p, i] for i in range(2) if (p, i) in self.columns)
                     for p in self.points}
        self.first = np.array([k in self.reference for k in self.keys])
        self.alpha = precision[0] * ARCSEC
        self.a_mm, self.b_ppm = precision[1:]
        self.obs_values, self.sigmas = [], []
        for k in self.keys:
            kind, a, b = k
            values = [r.value for r in self.groups[k]]
            if kind == "L":
                self.obs_values.append(angle(values[0]))
                self.sigmas.append(self.alpha)
            else:
                length = float(np.mean([float(v) for v in values]))
                self.obs_values.append(length)
                self.sigmas.append(math.hypot(self.a_mm, self.b_ppm * length / 1000)
                                   / (1000 * math.sqrt(2)))
        self.obs_values = np.array(self.obs_values)
        self.sigmas = np.array(self.sigmas)
        self.H = self.design(self.xy) / self.sigmas[:, None]

    def delta_row(self, a, b, derivative):
        row = np.zeros(self.u)
        for i, value in enumerate(derivative):
            if (b, i) in self.columns:
                row[self.columns[b, i]] += value
            if (a, i) in self.columns:
                row[self.columns[a, i]] -= value
        return row

    def baseline_row(self, a, b, xy):
        delta = xy[b] - xy[a]
        return self.delta_row(a, b, delta / np.linalg.norm(delta))

    def design(self, xy):
        rows = []
        for kind, a, b in self.keys:
            d = xy[b] - xy[a]
            if kind == "S":
                row = self.delta_row(a, b, d / np.linalg.norm(d))
            else:
                row = self.delta_row(a, b, np.array([-d[1], d[0]]) / (d @ d))
                row[self.ori[a]] = -0.001
            rows.append(row)
        return np.array(rows)

    def redundancy(self, n):
        return (n - self.u) / (n + self.azimuth_count)

    def requirements(self, cov):
        diagonal = np.diagonal(cov, axis1=-2, axis2=-1)
        mp = np.sqrt(np.stack([diagonal[..., idx].sum(axis=-1) for idx in self.sets.values()], axis=-1))
        var = np.einsum("pi,...ij,pj->...p", self.pairs_rows, cov, self.pairs_rows)
        ms = np.sqrt(np.maximum(var, 0))
        rel = ms / self.dist
        ratio = np.stack([mp.max(axis=-1), rel.max(axis=-1),
                          ms[..., self.longest], rel[..., self.longest]], axis=-1) / LIMITS
        return mp, ms, ratio

    def score(self, cov):
        mp, _, ratio = self.requirements(cov)
        return (0.76 * ratio.max(axis=-1) + 0.12 * ratio.mean(axis=-1)
                + 0.12 * mp.mean(axis=-1) / LIMITS[0])

    def active_edges(self, active):
        return [self.keys[i][1:] for i in active if self.keys[i][0] == "S"]

    def can_remove(self, active):
        degree = defaultdict(int)
        lon = defaultdict(int)
        edges = self.active_edges(active)
        for a, b in edges:
            degree[a] += 1
            degree[b] += 1
        for i in active:
            kind, a, b = self.keys[i]
            if kind == "L":
                lon[a] += 1
        for i in active:
            kind, a, b = self.keys[i]
            if kind == "L":
                if not self.first[i] and lon[a] > 3:
                    yield i
            elif degree[a] > 2 and degree[b] > 2:
                remain = [(u, v) for u, v in edges if (u, v) != (a, b)]
                if connected(remain, self.points) and cross_support(remain) >= 2:
                    yield i

    def select(self, base, target, seed, trials=42):
        size = min(range(self.u + 1, len(base) + 1), key=lambda n: abs(self.redundancy(n) - target))
        rng = np.random.default_rng(seed)
        starting_cov = np.linalg.inv(self.H[base].T @ self.H[base])
        best = None
        for trial in range(trials):
            active = list(base)
            cov = starting_cov.copy()
            while len(active) > size:
                ids = np.array(list(self.can_remove(active)), dtype=int)
                if not len(ids):
                    break
                h = self.H[ids]
                vh = h @ cov
                rem = 1 - np.einsum("ki,ki->k", vh, h)
                valid = rem > 0.01
                ids, vh, rem = ids[valid], vh[valid], rem[valid]
                if not len(ids):
                    break
                options = cov + np.einsum("ki,kj,k->kij", vh, vh, 1 / rem)
                value = self.score(options)
                if trial:
                    value += rng.uniform(0, [0.011, 0.023, 0.04][trial % 3], len(value))
                chosen = np.argmin(value)
                active.remove(ids[chosen])
                cov = options[chosen]
            if len(active) != size:
                continue
            idx = np.array(active, dtype=int)
            verify = np.linalg.inv(self.H[idx].T @ self.H[idx])
            score = self.score(verify)
            if best is None or score < best[0]:
                best = score, idx
        if best is None:
            raise RuntimeError(f"Cannot find a connected {size}-observation subset")
        return best[1]

    def extend_directions(self, base, target):
        """Preserve the distance geometry of the verified 0.55 layout."""
        size = min(range(len(base), len(self.keys) + 1),
                   key=lambda n: abs(self.redundancy(n) - target))
        active = list(base)
        available = [i for i, key in enumerate(self.keys)
                     if key[0] == "L" and i not in active]
        while len(active) < size:
            cov = np.linalg.inv(self.H[active].T @ self.H[active])
            h = self.H[available]
            hc = h @ cov
            gain = np.einsum("ij,ij->i", hc, h)
            options = cov - np.einsum("ki,kj,k->kij", hc, hc, 1 / (1 + gain))
            active.append(available.pop(int(np.argmin(self.score(options)))))
        return np.array(sorted(active), dtype=int)

    def adjustment(self, active):
        xy = {k: v.copy() for k, v in self.xy.items()}
        xy.update({k: v.copy() for k, v in self.fixed.items()})
        stations = {}
        for a, rs in self.stations.items():
            ref = next(r for r in rs if r.kind == "L")
            dx, dy = xy[ref.target] - xy[a]
            stations[a] = math.atan2(dy, dx) - angle(ref.value)
        def residual():
            readings = []
            for i in active:
                kind, a, b = self.keys[i]
                d = xy[b] - xy[a]
                v = self.obs_values[i]
                if kind == "L":
                    readings.append(wrap(v - math.atan2(d[1], d[0]) + stations[a]))
                else:
                    readings.append(v - np.linalg.norm(d))
            return np.array(readings)
        for _ in range(15):
            H = self.design(xy)[active] / self.sigmas[active, None]
            w = residual() / self.sigmas[active]
            delta, _, rank, _ = np.linalg.lstsq(H, w, rcond=None)
            if rank != self.u:
                raise ValueError("Rank deficient")
            for (p, d), col in self.columns.items():
                xy[p][d] += delta[col]
            for p, col in self.ori.items():
                stations[p] += 0.001 * delta[col]
            if np.max(np.abs(delta)) < 1e-8:
                break
        else:
            raise ValueError("Adjustment did not converge")
        H = self.design(xy)[active] / self.sigmas[active, None]
        cov = np.linalg.inv(H.T @ H)
        w = residual() / self.sigmas[active]
        sigma = math.sqrt((w @ w) / (len(active) - self.u))
        return cov, sigma, xy

    def report(self, active):
        H = self.H[active]
        cov = np.linalg.inv(H.T @ H)
        mp, ms, ratio = self.requirements(cov)
        weakest = np.argmax(ms / self.dist)
        worst = np.argmax(mp)
        count = len(active)
        distances = self.active_edges(active)
        cover = len(distances)
        r = 1 - np.einsum("ij,ij->i", H @ cov, H)
        _, sigma, _ = self.adjustment(active)
        longest = self.longest
        return {
            "实际平均冗余": self.redundancy(count), "方向数": count - cover, "距离边数": cover,
            "最弱点": self.points[worst], "点位中误差_mm": mp[worst] * 1000,
            "最弱边": "–".join(self.pairs[weakest]), "最弱边中误差_mm": ms[weakest] * 1000,
            "最弱边相对精度分母": self.dist[weakest] / ms[weakest],
            "最远点对": "–".join(self.pairs[longest]), "最远距离_m": self.dist[longest],
            "最远点间中误差_mm": ms[longest] * 1000,
            "最远点间相对精度分母": self.dist[longest] / ms[longest],
            "相对单位权中误差": sigma,
            "最小单项冗余": float(r.min()),
            "跨岸距离边数": sum((a in SHORE) != (b in SHORE) for a, b in distances),
            "平均保留边长_m": float(np.mean([np.linalg.norm(self.xy[a] - self.xy[b])
                                             for a, b in distances])),
            "精度指标判定": "达标" if np.all(ratio <= 1) and ratio[1] < 1 and ratio[3] < 1 else "未达标"
        }

    def validate_cosa_initial(self):
        report = self.source.with_suffix(".ou2").read_text(encoding="gbk", errors="replace")
        # The displayed distance precisions in COSA are rounded to 0.01 cm.
        section = report.split("距离平差结果")[1].split("平差坐标")[0]
        checked = 0
        for line in section.splitlines():
            fields = line.split()
            if len(fields) >= 8 and fields[2] == "S":
                key = ("S", *PAIR(*fields[:2]))
                observed_sigma = float(fields[4]) / 100
                if abs(observed_sigma - self.sigmas[self.keys.index(key)]) > 0.0000501:
                    raise ValueError(f"COSA distance weight mismatch: {key}")
                checked += 1
        if checked != 35:
            raise ValueError(f"Expected 35 COSA distance weights. Found {checked}.")
        match = re.search(r"后验单位权中误差\s*[:：]\s*([\d.]+)", report)
        _, sigma, _ = self.adjustment(np.arange(len(self.keys)))
        if not match or abs(float(match[1]) - sigma * 1.8) > 0.015:
            raise ValueError(f"COSA unit-weight cross-check failed: {sigma * 1.8}")
        return float(match[1])

    def write_in2(self, path, active):
        keep = {self.keys[i] for i in active}
        out = [*self.header, ""]
        for name, rows in self.stations.items():
            out.append(name)
            out.extend(rec.line for rec in rows if rec.kind == "A" or rec.key in keep)
            out.append("")
        payload = "\r\n".join(out)
        path.write_bytes(payload.encode("ascii"))


def connected(edges, points):
    neighbours = defaultdict(set)
    for a, b in edges:
        neighbours[a].add(b)
        neighbours[b].add(a)
    stack, reached = [points[0]], {points[0]}
    while stack:
        added = neighbours[stack.pop()] - reached
        reached.update(added)
        stack.extend(added)
    return len(reached) == len(points)


def cross_support(edges):
    sides = [set(), set()]
    for a, b in edges:
        if (a in SHORE) != (b in SHORE):
            sides[0 if a in SHORE else 1].add(a)
            sides[0 if b in SHORE else 1].add(b)
    return min(map(len, sides))


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]))
        out.writeheader()
        out.writerows(rows)


def main(root):
    base = root / "08_COSA数据及结果"
    with (base / "九点坐标对照.csv").open(encoding="utf-8-sig") as f:
        xy = {r["点号"]: np.array([float(r["独立坐标X_m"]), float(r["独立坐标Y_m"])])
              for r in csv.DictReader(f)}
    results, deleted = [], []
    configs = [
        ("固定两点", "固定QZ1和QZ2", 0, 26112601),
        ("固定一点一方向", "固定一点一方向", 1, 26112602),
    ]
    for label, suffix, az_cnt, seed in configs:
        net = Network(base / f"湘江九点初始网_{suffix}.in2", xy, az_cnt)
        full = np.arange(len(net.keys), dtype=int)
        ref = net.validate_cosa_initial()
        print(f"{label} COSA initial posterior unit weight: {ref} arcsec", flush=True)
        stage1 = net.select(full, 0.60, seed)
        stage2 = net.select(stage1, 0.55, seed + 10)
        if az_cnt:
            # COSAWIN98 failed to initialize the original single-datum 0.60
            # subset. The verified 0.60 input was built by extending the original
            # 0.55 selection with directions.
            stage1 = net.extend_directions(stage2, 0.60)
            # The approved redesign removes whole links from that verified input.
            stage2 = np.array([i for i in stage1
                               if PAIR(*net.keys[i][1:]) not in SINGLE_DATUM_SECOND_STAGE_REMOVED_PAIRS])
        prev = full
        for stage, target, active, folder in [
            ("初始方案", None, full, None),
            ("第一次优化", .60, stage1, "04_第一次优化"),
            ("第二次优化", .55, stage2, "05_第二次优化"),
        ]:
            data = net.report(active)
            result = {"阶段": stage, "基准": label, "目标": target, **data}
            result = {k: round(v, 6) if isinstance(v, float) else v for k, v in result.items()}
            results.append(result)
            print(result, flush=True)
            if folder is not None:
                dest = root / folder
                dest.mkdir(exist_ok=True)
                out = dest / f"湘江九点_{stage}_{suffix}.in2"
                net.write_in2(out, active)
                NetworkSubset.verify(out, net, active)
                for i in sorted(set(prev) - set(active)):
                    kind, a, b = net.keys[i]
                    deleted.append({"阶段": stage, "基准": label,
                                    "类型": "单站方向" if kind == "L" else "双端测距边",
                                    "测站或端点1": a, "照准点或端点2": b})
            prev = active
    index = {stage: i for i, stage in enumerate(("初始方案", "第一次优化", "第二次优化"))}
    results.sort(key=lambda row: index[row["阶段"]])
    dest = root / "06_精度评定"
    dest.mkdir(exist_ok=True)
    write_csv(dest / "六组方案先验精度对比.csv", results)
    write_csv(dest / "观测删减明细.csv", deleted)


class NetworkSubset:
    @staticmethod
    def verify(path, net, active):
        got = path.read_text(encoding="ascii").splitlines()
        want = [*net.header, ""]
        selected = {net.keys[i] for i in active}
        for sta, recs in net.stations.items():
            want.append(sta)
            want.extend(r.line for r in recs if r.kind == "A" or r.key in selected)
            want.append("")
        if got != want[:-1]:
            raise ValueError(f"Written observations differ from source subset: {path}")
        if len([line for line in got if ",L," in line]) != sum(k[0] == "L" for k in selected):
            raise ValueError("Direction count mismatch")
        if len([line for line in got if ",S," in line]) != 2 * sum(k[0] == "S" for k in selected):
            raise ValueError("Distance count mismatch")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path(__file__).resolve().parent.parent)
    main(parser.parse_args().root)
