# -*- coding: utf-8 -*-
"""下载并拼接卫星影像瓦片(Esri World Imagery), 用于控制网布设"""
import math
import os
import sys
import time
import urllib.request

from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\31710\OneDrive\Desktop\测量数据\控制网设计\imagery"
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def lonlat_to_tile(lon, lat, z):
    n = 2 ** z
    x = (lon + 180.0) / 360.0 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 /
                      math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def tile_to_lonlat(x, y, z):
    n = 2 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def fetch(z, x, y, cache=True):
    fn = os.path.join(OUT, f"t_{z}_{x}_{y}.jpg")
    if cache and os.path.exists(fn) and os.path.getsize(fn) > 500:
        return fn
    url = (f"https://server.arcgisonline.com/ArcGIS/rest/services/"
           f"World_Imagery/MapServer/tile/{z}/{y}/{x}")
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=40).read()
    with open(fn, "wb") as f:
        f.write(data)
    return fn


def mosaic(lon, lat, z, nx, ny, name):
    cx, cy = lonlat_to_tile(lon, lat, z)
    x0 = int(cx) - nx // 2
    y0 = int(cy) - ny // 2
    W = nx * 256
    H = ny * 256
    img = Image.new("RGB", (W, H))
    for j in range(ny):
        for i in range(nx):
            fn = fetch(z, x0 + i, y0 + j)
            im = Image.open(fn).convert("RGB")
            img.paste(im, (i * 256, j * 256))
            time.sleep(0.02)
    out = os.path.join(OUT, name)
    img.save(out, quality=92)
    # 记录地理范围
    lon0, lat0 = tile_to_lonlat(x0, y0 + ny, z)
    lon1, lat1 = tile_to_lonlat(x0 + nx, y0, z)
    print(f"{name}: z={z} tiles x{x0}-{x0+nx-1} y{y0}-{y0+ny-1}")
    print(f"   经度 {lon0:.6f} ~ {lon1:.6f}   纬度 {lat0:.6f} ~ {lat1:.6f}")
    print(f"   像素 {W}x{H}  米/像素 {156543.03392*math.cos(math.radians(lat))/2**z:.2f}")
    return out, (x0, y0, z, nx, ny)


if __name__ == "__main__":
    # 湘潭市区 湘江 一带
    mosaic(112.945, 27.870, 14, 6, 5, "m_z14.jpg")
