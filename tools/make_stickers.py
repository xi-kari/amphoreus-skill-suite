# -*- coding: utf-8 -*-
"""表情包归一化管线:从委托人提供的原图目录生成 assets/stickers/ 下的 ASCII 键名 PNG,
并写出 assets/stickers/manifest.js(window.STICKERS,三个页面表情包墙的单源)与 manifest.json;
同时为全部 96 枚(含 18 枚默认头像)生成 assets/stickers/w/<key>.webp 显示件(最长边 256,q88),页面与 README 只引用显示件。

用法:python tools/make_stickers.py [--src "D:/研究/表情包"] [--max 512] [--check]
  --check  只回对:manifest 中每个文件都存在、尺寸 <= max、无孤儿文件(不写任何东西)

归一化规则:最长边 > MAX 的按 LANCZOS 缩到 MAX,<= MAX 的原字节保留;
2026-08-31 批次的 18 枚默认头像(<key>.png)不在本脚本管辖内,原字节不动。
"""
import argparse
import hashlib
import json
import os
import shutil
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "assets", "stickers")
WEB = os.path.join(OUT, "w")          # 显示件:最长边 WEB_MAX 的 WebP(页面与 README 引用)
WEB_MAX = 256
WEB_Q = 88

# 角色键名(与 skills/、index.html ORDER 同源)
HEROES = {
    "aglaea": "阿格莱雅", "tribbie": "缇宝", "mydei": "万敌", "castorice": "遐蝶", "anaxa": "那刻夏",
    "hyacine": "风堇", "cipher": "赛飞儿", "cerydra": "刻律德菈", "hysilens": "海瑟音",
    "march7th": "三月七", "terrae": "丹恒", "phainon": "白厄", "cyrene": "昔涟",
    "trailblazer-stelle": "开拓者·星", "trailblazer-caelus": "开拓者·穹",
}

# 源文件名(不含 .png) -> (输出键名, 所属角色键, 中文情绪标签, 附注)
# 2026-09-02 批次 78 枚。奇美拉 = 各黄金裔的伙伴小兽,迷迷 = 风堇的伙伴,小昔涟 = 昔涟幼年。
MAP = {
    "万敌-健身": ("mydei-workout", "mydei", "健身", ""),
    "万敌-吃什么": ("mydei-what-to-eat", "mydei", "吃什么", ""),
    "万敌-狂": ("mydei-frenzy", "mydei", "狂", ""),
    "万敌-红温": ("mydei-flushed", "mydei", "红温", ""),
    "丹恒-倾听": ("terrae-listen", "terrae", "倾听", ""),
    "丹恒-大地之王": ("terrae-king-of-earth", "terrae", "大地之王", ""),
    "丹恒-拍照": ("terrae-photo", "terrae", "拍照", ""),
    "丹恒-欲言又止": ("terrae-hesitate", "terrae", "欲言又止", ""),
    "刻律德菈-公平": ("cerydra-fair", "cerydra", "公平", ""),
    "刻律德菈-再说一遍": ("cerydra-say-again", "cerydra", "再说一遍", ""),
    "刻律德菈-否决": ("cerydra-veto", "cerydra", "否决", ""),
    "刻律德菈-将军": ("cerydra-checkmate", "cerydra", "将军", ""),
    "奇美拉-万敌-蜜果羹-再战": ("chimera-mydei", "mydei", "再战", "蜜果羹"),
    "奇美拉-丹恒-暖龙龙-保护": ("chimera-terrae", "terrae", "保护", "暖龙龙"),
    "奇美拉-刻律德菈-奇兽爵-直视": ("chimera-cerydra", "cerydra", "直视", "奇兽爵"),
    "奇美拉-海瑟音-咕噜鱼儿-听歌": ("chimera-hysilens", "hysilens", "听歌", "咕噜鱼儿"),
    "奇美拉-白厄-比格椰-不知道": ("chimera-phainon", "phainon", "不知道", "比格椰"),
    "奇美拉-缇宝-苹果糖-炸飞": ("chimera-tribbie", "tribbie", "炸飞", "苹果糖"),
    "奇美拉-赛飞儿-喵咪神偷-夸夸": ("chimera-cipher", "cipher", "夸夸", "喵咪神偷"),
    "奇美拉-遐蝶-蝶糕糕-起飞": ("chimera-castorice", "castorice", "起飞", "蝶糕糕"),
    "奇美拉-那刻夏-努努斯-喜爱": ("chimera-anaxa", "anaxa", "喜爱", "努努斯"),
    "奇美拉-长夜月-胶糖卷-捕捉": ("chimera-march7th", "march7th", "捕捉", "胶糖卷"),
    "奇美拉-阿格莱雅-燕麦粥-缠绕": ("chimera-aglaea", "aglaea", "缠绕", "燕麦粥"),
    "奇美拉-风堇-车厘比斯-安抚": ("chimera-hyacine", "hyacine", "安抚", "车厘比斯"),
    "小昔涟-嘻嘻": ("cyrene-young-hehe", "cyrene", "嘻嘻", "小昔涟"),
    "开拓者女-记录": ("trailblazer-stelle-record", "trailblazer-stelle", "记录", ""),
    "开拓者女-重写": ("trailblazer-stelle-rewrite", "trailblazer-stelle", "重写", ""),
    "开拓者男-记录": ("trailblazer-caelus-record", "trailblazer-caelus", "记录", ""),
    "开拓者男-重写": ("trailblazer-caelus-rewrite", "trailblazer-caelus", "重写", ""),
    "昔涟-回眸": ("cyrene-glance", "cyrene", "回眸", ""),
    "昔涟-守护": ("cyrene-guard", "cyrene", "守护", ""),
    "昔涟-收到": ("cyrene-roger", "cyrene", "收到", ""),
    "昔涟-爱": ("cyrene-love", "cyrene", "爱", ""),
    "海瑟音-共舞": ("hysilens-dance", "hysilens", "共舞", ""),
    "海瑟音-哼歌": ("hysilens-humming", "hysilens", "哼歌", ""),
    "海瑟音-嘘": ("hysilens-shh", "hysilens", "嘘", ""),
    "海瑟音-忠诚": ("hysilens-loyalty", "hysilens", "忠诚", ""),
    "白厄-再见": ("phainon-bye", "phainon", "再见", ""),
    "白厄-我吗": ("phainon-me", "phainon", "我吗", ""),
    "白厄-战斗": ("phainon-fight", "phainon", "战斗", ""),
    "白厄-掉线": ("phainon-offline", "phainon", "掉线", ""),
    "白厄-没事": ("phainon-fine", "phainon", "没事", ""),
    "白厄-诶嘿": ("phainon-ehe", "phainon", "诶嘿", ""),
    "缇宁-发送": ("tribbie-ning-send", "tribbie", "发送", "缇宁"),
    "缇安-晚安": ("tribbie-an-goodnight", "tribbie", "晚安", "缇安"),
    "缇宝-炸飞": ("tribbie-boom", "tribbie", "炸飞", ""),
    "缇宝-睿智": ("tribbie-wise", "tribbie", "睿智", ""),
    "赛飞儿-可爱": ("cipher-cute", "cipher", "可爱", ""),
    "赛飞儿-得手": ("cipher-gotcha", "cipher", "得手", ""),
    "赛飞儿-招财": ("cipher-fortune", "cipher", "招财", ""),
    "赛飞儿-拜托": ("cipher-please", "cipher", "拜托", ""),
    "迷迷-哭": ("mimi-cry", "hyacine", "哭", "迷迷"),
    "迷迷-心心": ("mimi-hearts", "hyacine", "心心", "迷迷"),
    "迷迷-我来": ("mimi-my-turn", "hyacine", "我来", "迷迷"),
    "迷迷-抱": ("mimi-hug", "hyacine", "抱", "迷迷"),
    "迷迷-攻击": ("mimi-attack", "hyacine", "攻击", "迷迷"),
    "迷迷-睡觉": ("mimi-sleep", "hyacine", "睡觉", "迷迷"),
    "遐蝶-不了": ("castorice-no-thanks", "castorice", "不了", ""),
    "遐蝶-创作": ("castorice-create", "castorice", "创作", ""),
    "遐蝶-枯萎": ("castorice-wither", "castorice", "枯萎", ""),
    "遐蝶-脸红": ("castorice-blush", "castorice", "脸红", ""),
    "遐蝶-蝴蝶": ("castorice-butterfly", "castorice", "蝴蝶", ""),
    "那刻夏-什么事": ("anaxa-what", "anaxa", "什么事", ""),
    "那刻夏-我没事": ("anaxa-im-fine", "anaxa", "我没事", ""),
    "那刻夏-来吧": ("anaxa-bring-it", "anaxa", "来吧", ""),
    "那刻夏-看穿": ("anaxa-see-through", "anaxa", "看穿", ""),
    "长夜月-去吧": ("march7th-evernight-go", "march7th", "去吧", "长夜月"),
    "长夜月-嚎啕大哭": ("march7th-evernight-wail", "march7th", "嚎啕大哭", "长夜月"),
    "长夜月-暗示": ("march7th-evernight-hint", "march7th", "暗示", "长夜月"),
    "长夜月-警告": ("march7th-evernight-warning", "march7th", "警告", "长夜月"),
    "阿格莱雅-不": ("aglaea-no", "aglaea", "不", ""),
    "阿格莱雅-慷慨": ("aglaea-generous", "aglaea", "慷慨", ""),
    "阿格莱雅-泡澡": ("aglaea-bath", "aglaea", "泡澡", ""),
    "阿格莱雅-设计": ("aglaea-design", "aglaea", "设计", ""),
    "风堇-喜欢": ("hyacine-like", "hyacine", "喜欢", ""),
    "风堇-治愈": ("hyacine-heal", "hyacine", "治愈", ""),
    "风堇-诊断": ("hyacine-diagnose", "hyacine", "诊断", ""),
    "风堇-试试看": ("hyacine-try", "hyacine", "试试看", ""),
}

# 2026-08-31 批次 18 枚默认头像(原字节,不经本脚本):key -> (owner, label, note)
BASE = {
    "aglaea": ("aglaea", "阿格莱雅", ""), "anaxa": ("anaxa", "那刻夏", ""), "castorice": ("castorice", "遐蝶", ""),
    "cerydra": ("cerydra", "刻律德菈", ""), "cipher": ("cipher", "赛飞儿", ""), "cyrene": ("cyrene", "昔涟", ""),
    "hyacine": ("hyacine", "风堇", ""), "hysilens": ("hysilens", "海瑟音", ""), "march7th": ("march7th", "三月七", ""),
    "march7th-evernight": ("march7th", "长夜月", "长夜月"), "mydei": ("mydei", "万敌", ""), "phainon": ("phainon", "白厄", ""),
    "terrae": ("terrae", "丹恒", ""), "trailblazer-caelus": ("trailblazer-caelus", "开拓者·穹", ""),
    "trailblazer-stelle": ("trailblazer-stelle", "开拓者·星", ""), "tribbie": ("tribbie", "缇宝", ""),
    "tribbie-an": ("tribbie", "缇安", "缇安"), "tribbie-ning": ("tribbie", "缇宁", "缇宁"),
}


def sha12(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()[:12]


def kind_of(key):
    if key.startswith("chimera-") or key.startswith("mimi-") or key.startswith("cyrene-young"):
        return "companion"
    return "mood"


def webp(src_png, key):
    """从 PNG(存档件)生成显示件 w/<key>.webp,最长边 WEB_MAX,q=WEB_Q。"""
    os.makedirs(WEB, exist_ok=True)
    im = Image.open(src_png).convert("RGBA")
    w, h = im.size
    if max(w, h) > WEB_MAX:
        s = WEB_MAX / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    dst = os.path.join(WEB, key + ".webp")
    im.save(dst, "WEBP", quality=WEB_Q, method=6)
    return os.path.getsize(dst)


def build(src, mx):
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for k in BASE:
        webp(os.path.join(OUT, k + ".png"), k)
    for zh, (key, owner, mood, note) in MAP.items():
        sp = os.path.join(src, zh + ".png")
        if not os.path.exists(sp):
            print("MISSING", sp)
            sys.exit(2)
        im = Image.open(sp)
        im.load()
        w, h = im.size
        dst = os.path.join(OUT, key + ".png")
        if max(w, h) > mx:
            im = im.convert("RGBA")
            s = mx / max(w, h)
            im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
            im.save(dst, "PNG", optimize=True)
            how = "%dx%d->%dx%d" % (w, h, im.size[0], im.size[1])
        else:
            shutil.copyfile(sp, dst)
            how = "%dx%d raw" % (w, h)
        wk = webp(dst, key)
        rows.append((key, owner, mood, note, zh))
        print("%-32s %-24s %4dKB  webp %3dKB  <- %s" % (key, how, os.path.getsize(dst) // 1024, wk // 1024, zh))
    return rows


def manifest(rows):
    items = []
    for k, (owner, label, note) in BASE.items():
        items.append({"key": k, "owner": owner, "label": label, "note": note, "batch": "2026-08-31", "kind": "base"})
    for key, owner, mood, note, zh in rows:
        items.append({"key": key, "owner": owner, "label": mood, "note": note, "batch": "2026-09-02",
                      "kind": kind_of(key), "src": zh})
    heroes = [{"key": k, "name": v} for k, v in HEROES.items()]
    data = {"heroes": heroes, "items": items, "count": len(items)}
    js = ("/* 由 tools/make_stickers.py 生成,勿手改。window.STICKERS = {heroes, items, count}\n"
          "   items[].key = assets/stickers/<key>.png;owner = 所属角色键;"
          "kind = base(默认头像)/mood(表情)/companion(伙伴:奇美拉、迷迷、小昔涟) */\n"
          "window.STICKERS=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
    with open(os.path.join(OUT, "manifest.js"), "w", encoding="utf-8", newline="\n") as f:
        f.write(js)
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("manifest:", len(items), "items")


def check(mx):
    data = json.load(open(os.path.join(OUT, "manifest.json"), encoding="utf-8"))
    keys = {it["key"] for it in data["items"]}
    bad = 0
    for it in data["items"]:
        p = os.path.join(OUT, it["key"] + ".png")
        if not os.path.exists(p):
            print("MISSING FILE", p)
            bad += 1
            continue
        w, h = Image.open(p).size
        if max(w, h) > mx:
            print("OVERSIZE", p, w, h)
            bad += 1
        wp = os.path.join(WEB, it["key"] + ".webp")
        if not os.path.exists(wp):
            print("MISSING WEBP", wp)
            bad += 1
        elif max(Image.open(wp).size) > WEB_MAX:
            print("OVERSIZE WEBP", wp)
            bad += 1
        if it["owner"] not in HEROES:
            print("BAD OWNER", it)
            bad += 1
    for f in os.listdir(OUT):
        if f.endswith(".png") and f[:-4] not in keys:
            print("ORPHAN", f)
            bad += 1
    for f in os.listdir(WEB):
        if f.endswith(".webp") and f[:-5] not in keys:
            print("ORPHAN WEBP", f)
            bad += 1
    # manifest.js 与 manifest.json 同步
    js = open(os.path.join(OUT, "manifest.js"), encoding="utf-8").read()
    if json.dumps(data, ensure_ascii=False, separators=(",", ":")) not in js:
        print("MANIFEST.JS OUT OF SYNC")
        bad += 1
    print("check:", "PASS" if not bad else "FAIL(%d)" % bad, "items=%d" % len(keys))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="D:/研究/表情包")
    ap.add_argument("--max", type=int, default=512)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if a.check:
        check(a.max)
    else:
        manifest(build(a.src, a.max))
