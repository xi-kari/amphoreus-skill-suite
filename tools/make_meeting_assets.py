# -*- coding: utf-8 -*-
"""全体会议页(meeting.html)图像资产管线。

输入为仓库外的英雄纪、如我所书卡牌与日历图集。
用 --hero-dir、--book-dir、--calendar-dir、--cover 指定输入路径;
未指定时,在 --src (默认仓库父目录)按图集名称后缀唯一匹配,
封面按 *一年历-封面-昔涟.jpg 唯一匹配。文件与目录名称不受项目名称 δ-me13 限制。
--check 只检查输入路径、数量与输出文件是否齐全,不创建目录或编码图片。

规则:等比缩宽、sRGB、WebP(method=6);输出统一落在 assets/meeting/。
键名与 cards.html 的 CARDS 键一致;三月七对应立绘为长夜月形态(03长夜月)。
"""
import argparse
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "meeting"

# 序号前缀 -> 站内键(阿格莱雅在英雄纪文件名写作「阿格莱呀」,按前缀匹配绕开)
NUM_KEY = {
    "01": "tribbie", "02": "cerydra", "03": "march7th", "04": "terrae",
    "05": "hysilens", "06": "hyacine", "07": "phainon", "08": "anaxa",
    "09": "aglaea", "10": "mydei", "11": "castorice", "12": "cipher", "13": "cyrene",
}
# 月份 -> 键(与月历文件名中的角色一致;封面为昔涟)
MONTH_KEY = {
    "1月": "tribbie", "2月": "cerydra", "3月": "march7th", "4月": "terrae",
    "5月": "hysilens", "6月": "hyacine", "7月": "phainon", "8月": "anaxa",
    "9月": "aglaea", "10月": "mydei", "11月": "castorice", "12月": "cipher",
}

def save(im: Image.Image, path: Path, width: int, quality: int):
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "transparency" in im.info or im.mode == "P" else "RGB")
    if im.mode == "RGBA":
        bg = Image.new("RGB", im.size, (244, 242, 248))
        bg.paste(im, mask=im.split()[3])
        im = bg
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(path, "WEBP", quality=quality, method=6)
    return path.stat().st_size

def unique_input(root: Path, pattern: str, directory: bool = True) -> Path:
    matches = sorted(p for p in root.glob(pattern) if (p.is_dir() if directory else p.is_file()))
    if len(matches) != 1:
        raise ValueError(f"输入需要唯一匹配: {root / pattern}; 找到 {len(matches)} 项,请显式指定路径")
    return matches[0]


def image_jobs(args):
    hero_dir = args.hero_dir or unique_input(args.src, "*英雄纪")
    book_dir = args.book_dir or unique_input(args.src, "*如我所书卡牌")
    cal_dir = args.calendar_dir or unique_input(args.src, "*日历")
    for directory in (hero_dir, book_dir, cal_dir):
        if not directory.is_dir():
            raise ValueError(f"输入目录不存在: {directory}")
    jobs = []
    for directory, pattern, prefix, quality in (
        (hero_dir, "*.jpg", "hero", 82), (book_dir, "*.png", "book", 85)
    ):
        files = sorted(directory.glob(pattern))
        if len(files) != 13 or {f.name[:2] for f in files} != set(NUM_KEY):
            raise ValueError(f"图集必须包含 01 至 13 各一张: {directory}")
        for f in files:
            jobs.append((f, OUT / f"{prefix}-{NUM_KEY[f.name[:2]]}.webp", 640, quality))
    months = sorted(cal_dir.glob("*月-*.jpg"))
    if len(months) != 12 or {f.name.split("-", 1)[0] for f in months} != set(MONTH_KEY):
        raise ValueError(f"日历必须包含 1 至 12 月各一张: {cal_dir}")
    for f in months:
        key = MONTH_KEY[f.name.split("-", 1)[0]]
        jobs.extend(((f, OUT / f"cal-{key}.webp", 420, 80),
                     (f, OUT / f"cal-{key}-full.webp", 1000, 82)))
    cover = args.cover or unique_input(cal_dir, "*一年历-封面-昔涟.jpg", directory=False)
    lunar = cal_dir / "2026阴历版本.jpeg"
    jobs.extend(((cover, OUT / "cal-cyrene.webp", 420, 80),
                 (cover, OUT / "cal-cyrene-full.webp", 1000, 82),
                 (lunar, OUT / "cal-lunar.webp", 1600, 80),
                 (lunar, OUT / "cal-lunar-full.webp", 2600, 82)))
    for source, _, _, _ in jobs:
        if not source.is_file():
            raise ValueError(f"输入文件不存在: {source}")
    return jobs


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, default=ROOT.parent, help="自动查找图集的父目录")
    parser.add_argument("--hero-dir", type=Path, help="13 张角色海报目录")
    parser.add_argument("--book-dir", type=Path, help="13 张角色卡面目录")
    parser.add_argument("--calendar-dir", type=Path, help="日历目录")
    parser.add_argument("--cover", type=Path, help="日历封面文件")
    parser.add_argument("--check", action="store_true", help="只读检查输入及 54 张输出是否齐全")
    args = parser.parse_args()
    try:
        jobs = image_jobs(args)
    except ValueError as exc:
        parser.error(str(exc))
    if args.check:
        missing = [str(target) for _, target, _, _ in jobs if not target.is_file()]
        if missing:
            parser.error("输出文件缺失: " + ", ".join(missing))
        print("OK: 40 inputs + 54 outputs present; no images encoded")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for source, target, width, quality in jobs:
        with Image.open(source) as im:
            n = save(im, target, width, quality)
        total += n
        print(f"{n/1024:8.1f} KB  {target.name}")
    print(f"OK: {len(jobs)} files, {total/1024/1024:.2f} MB total")

if __name__ == "__main__":
    run()
