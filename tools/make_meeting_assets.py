# -*- coding: utf-8 -*-
"""全体会议页(meeting.html)图像资产管线。

输入(委托人提供的官方图集,均在仓库外):
  D:/研究/翁法罗斯英雄纪/          13 张角色海报 jpg   -> hero-<key>.webp   (议题一/二 发言立绘)
  D:/研究/翁法罗斯如我所书卡牌/     13 张卡面 png       -> book-<key>.webp   (议题三 发言卡面)
  D:/研究/翁法罗斯日历/            13 张月历 + 1 张横版阴历全年历
                                   -> cal-<key>.webp / cal-<key>-full.webp / cal-lunar.webp (尾声年历画廊)

规则:等比缩宽、sRGB、WebP(method=6);输出统一落在 assets/meeting/。
键名与 cards.html 的 CARDS 键一致;三月七对应立绘为长夜月形态(03长夜月)。
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("D:/研究")
OUT = ROOT / "assets" / "meeting"
OUT.mkdir(parents=True, exist_ok=True)

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

def run():
    total = 0
    report = []

    hero_dir = SRC / "翁法罗斯英雄纪"
    for f in sorted(hero_dir.glob("*.jpg")):
        key = NUM_KEY[f.name[:2]]
        n = save(Image.open(f), OUT / f"hero-{key}.webp", 640, 82)
        total += n; report.append((f"hero-{key}.webp", n))

    book_dir = SRC / "翁法罗斯如我所书卡牌"
    for f in sorted(book_dir.glob("*.png")):
        key = NUM_KEY[f.name[:2]]
        n = save(Image.open(f), OUT / f"book-{key}.webp", 640, 85)
        total += n; report.append((f"book-{key}.webp", n))

    cal_dir = SRC / "翁法罗斯日历"
    for f in sorted(cal_dir.glob("*月-*.jpg")):
        month = f.name.split("-", 1)[0]
        key = MONTH_KEY[month]
        im = Image.open(f)
        n = save(im, OUT / f"cal-{key}.webp", 420, 80)
        m = save(Image.open(f), OUT / f"cal-{key}-full.webp", 1000, 82)
        total += n + m; report.append((f"cal-{key}(.thumb+full)", n + m))
    cover = cal_dir / "翁法罗斯2026一年历-封面-昔涟.jpg"
    n = save(Image.open(cover), OUT / "cal-cyrene.webp", 420, 80)
    m = save(Image.open(cover), OUT / "cal-cyrene-full.webp", 1000, 82)
    total += n + m; report.append(("cal-cyrene(.thumb+full)", n + m))
    lunar = cal_dir / "2026阴历版本.jpeg"
    n = save(Image.open(lunar), OUT / "cal-lunar.webp", 1600, 80)
    m = save(Image.open(lunar), OUT / "cal-lunar-full.webp", 2600, 82)
    total += n + m; report.append(("cal-lunar(+full)", n + m))

    for name, n in report:
        print(f"{n/1024:8.1f} KB  {name}")
    files = sorted(OUT.glob("*.webp"))
    print(f"-- {len(files)} files, {total/1024/1024:.2f} MB total")
    # 完整性:hero/book 各 13;cal 缩略+full 各 13(12 月 + 封面昔涟);阴历版两档
    keys = set(NUM_KEY.values())
    heroes = {p.stem[5:] for p in OUT.glob("hero-*.webp")}
    books = {p.stem[5:] for p in OUT.glob("book-*.webp")}
    cal_full = {p.stem[4:-5] for p in OUT.glob("cal-*-full.webp") if p.stem != "cal-lunar-full"}
    cal_thumb = {p.stem[4:] for p in OUT.glob("cal-*.webp")
                 if not p.stem.endswith("-full") and p.stem != "cal-lunar"}
    assert heroes == keys == books, (heroes, books)
    assert cal_thumb == keys == cal_full, (cal_thumb, cal_full)
    assert (OUT / "cal-lunar.webp").exists() and (OUT / "cal-lunar-full.webp").exists()
    print("OK: 13 hero + 13 book + 13+13 calendar + lunar×2 complete")

if __name__ == "__main__":
    run()
