#!/usr/bin/env python3
"""黄金裔徽记裁切:对每张「逐火者的命录」卡面原图做圆检测,居中截取顶部徽记。

取代 make_layers.py 里的固定几何常数(cx=0.4975W, cy=0.0894W, side=0.115W)——
该常数在多数卡上整体偏下、截不成正圆;此处改为逐卡 HoughCircles 定位。

用法:python tools/crop_symbols.py            # 读 assets/cards-full/,写 assets/symbols/
依赖:pip install opencv-python pillow numpy
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "cards-full"
DST = ROOT / "assets" / "symbols"
OUT = 240          # 输出边长
MARGIN = 1.10      # 裁切半边 = 检测半径 × MARGIN,给金环外留一圈呼吸
KEYS = [
    "aglaea", "cerydra", "terrae", "phainon", "anaxa", "cipher", "hyacine",
    "march7th", "castorice", "cyrene", "mydei", "hysilens", "tribbie",
    "trailblazer-stelle", "trailblazer-caelus",
]


def detect(img: np.ndarray, w0: int):
    """在顶部正中窗口内找徽记圆,返回全图坐标 (cx, cy, r);找不到返回 None。"""
    x0, x1 = int(0.30 * w0), int(0.70 * w0)
    y1 = int(0.20 * w0)
    win = cv2.cvtColor(img[0:y1, x0:x1], cv2.COLOR_BGR2GRAY)
    win = cv2.medianBlur(win, 5)
    r_lo, r_hi = int(0.045 * w0), int(0.078 * w0)
    for p2 in (0.9, 0.8, 0.7):          # 逐步放宽圆度阈值
        circles = cv2.HoughCircles(
            win, cv2.HOUGH_GRADIENT_ALT, dp=1.5, minDist=w0,
            param1=200, param2=p2, minRadius=r_lo, maxRadius=r_hi)
        if circles is not None:
            cx, cy, r = circles[0][0]
            return float(cx) + x0, float(cy), float(r)
    return None


def main() -> None:
    DST.mkdir(parents=True, exist_ok=True)
    report = []
    for k in KEYS:
        p = SRC / f"{k}.png"
        img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)  # 路径可含中文
        h0, w0 = img.shape[:2]
        hit = detect(img, w0)
        if hit is None:
            print(f"{k}: DETECT FAILED — 保留旧文件"); continue
        cx, cy, r = hit
        half = r * MARGIN
        box = (round(cx - half), round(cy - half), round(cx + half), round(cy + half))
        pil = Image.open(p).convert("RGB").crop(box).resize((OUT, OUT), Image.LANCZOS)
        pil.save(DST / f"{k}.png", optimize=True)
        report.append((k, cx / w0, cy / w0, r / w0))
        print(f"{k:20s} cx={cx/w0:.4f}W cy={cy/w0:.4f}W r={r/w0:.4f}W box={box}")
    if report:
        arr = np.array([[c, y, r] for _, c, y, r in report])
        print(f"median: cx={np.median(arr[:,0]):.4f}W cy={np.median(arr[:,1]):.4f}W r={np.median(arr[:,2]):.4f}W")


if __name__ == "__main__":
    main()
