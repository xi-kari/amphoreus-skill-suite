#!/usr/bin/env python3
"""闪卡分层管线:从「逐火者的命录」卡面原图产出视差分层素材。

层序(对应真实卡片的物理纵深,cards.html 消费):
  assets/layers/<k>-base.webp   底片层 = 完整卡面(640px)
  assets/layers/<k>-front.webp  前景层 = 金属边框+人物,拱窗内背景透空(rembg isnet-general-use 整卡抠像)
  assets/symbols/<k>.png        徽记层 = 由 tools/crop_symbols.py 逐卡圆检测裁切(旧固定常数整体偏下,已废弃)
  assets/layers/sparkle.png     星屑贴图(程序生成,平铺)

依赖:pip install rembg onnxruntime pillow
用法:python tools/make_layers.py <原图目录>   # 原图 = patchwiki 原尺寸 PNG(去 thumb 路径),文件名 <k>.png

说明:曾试验第三层「窗内人物单抠」(拱窗裁剪后再抠像),15 张中过半出现半透明鬼影与碎裂,弃用;
两图层+徽记+CSS 箔光已能成立体闪卡。u2net 对此类新艺术风卡面几乎整卡保留,故选 isnet。
"""
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove

KEYS = [
    "aglaea", "cerydra", "terrae", "phainon", "anaxa", "cipher", "hyacine",
    "march7th", "castorice", "cyrene", "mydei", "hysilens", "tribbie",
    "trailblazer-stelle", "trailblazer-caelus",
]
ROOT = Path(__file__).resolve().parent.parent
LAYERS = ROOT / "assets" / "layers"
SYMBOLS = ROOT / "assets" / "symbols"
W = 640


def main(src_dir: str) -> None:
    src = Path(src_dir)
    LAYERS.mkdir(parents=True, exist_ok=True)
    SYMBOLS.mkdir(parents=True, exist_ok=True)
    sess = new_session("isnet-general-use")
    for k in KEYS:
        im = Image.open(src / f"{k}.png").convert("RGB")
        w0, h0 = im.size
        # 底片层
        base = im.resize((W, round(h0 * W / w0)), Image.LANCZOS)
        base.save(LAYERS / f"{k}-base.webp", quality=78, method=6)
        # 前景层(800px 入模型,640px 出图)
        im8 = im.resize((800, round(h0 * 800 / w0)), Image.LANCZOS)
        front = remove(im8, session=sess)
        front = front.resize((W, round(front.height * W / front.width)), Image.LANCZOS)
        front.save(LAYERS / f"{k}-front.webp", quality=75, method=6)
        # 徽记层由 tools/crop_symbols.py 圆检测另行产出,此处不再裁切
        print(k, "ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "cardfull")
