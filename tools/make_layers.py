#!/usr/bin/env python3
"""闪卡分层管线 v2:把「逐火者的命录」卡面拆成三个互斥分区层,正面合成逐像素还原原图。

层序(对应真实卡片物理纵深,cards.html 消费):
  assets/layers/<k>-back.webp   背景层 = 完整画布不透明;被前景/徽记盖住的区域用邻域修补填充,
                                正视时被上层精确遮住,只有倾斜(视差)时露出——露出的是背景延续,不是内容拷贝
  assets/layers/<k>-front.webp  前景层 = 金属边框+人物 RGBA 抠像(rembg isnet-general-use),
                                徽记圆片区域挖空(该内容归徽记层,杜绝重复)
  assets/layers/<k>-crest.webp  徽记层 = 逐卡 HoughCircles 定位裁出的圆片(1.5px 羽化)
  assets/layers/geo.js          页面几何单源(cards.html 以 <script src> 消费,杜绝内联双源漂移)
  assets/layers/manifest.json   同一几何的存档副本(含质检指标)
  assets/layers/sparkle.png     星屑贴图(程序生成,沿用)

分区不变量(v1 重影的根因即违反此点——底片层是完整卡面,与前景层内容重复):
  1) 任何画面内容只归一层:alpha 近二值(实心/透空 + ≤4px 抗锯齿边带);抠像模型在纹样密集区
     (如 hysilens 底部铭牌)给出的大面积摇摆中间值,静止合成断言天然抓不到(a·orig+(1-a)·orig==orig),
     倾斜时同一内容两层各现一份 → 由 harden_alpha() 区域级归并:成片不稳定区整块划归前景,
     背景该处必被修补;
  2) 静止合成 crest∘front∘back == 原图:内存数组逐像素断言(≤3 灰阶),编码落盘后再解码复验
     (webp 有损噪声阈内);边带处背景保持原图,任意混合权重仍还原原图。

依赖:pip install rembg onnxruntime opencv-python pillow numpy
用法:python tools/make_layers.py            # 读 assets/cards-full/,写 assets/layers/ 与 tools/qa_out/
"""
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from crop_symbols import detect  # 逐卡徽记圆检测(全图坐标 cx, cy, r)

KEYS = [
    "aglaea", "cerydra", "terrae", "phainon", "anaxa", "cipher", "hyacine",
    "march7th", "castorice", "cyrene", "mydei", "hysilens", "tribbie",
    "trailblazer-stelle", "trailblazer-caelus",
]
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "cards-full"
LAYERS = ROOT / "assets" / "layers"
QA = ROOT / "tools" / "qa_out"
W = 768                 # 层宽(约两倍于画廊展示宽,兼顾清晰与体积)
MATTE_W = 1024          # 抠像输入宽
CREST_MARGIN = 1.06     # 圆片裁切半径 = 检测半径 × 该系数(含金环外缘)
SPECK = 4e-4            # 前景 alpha 清理:小于画布面积此比例的孤岛/针孔
AMB_AREA = 600          # 不稳定区归并的最小成片面积(px)


def load_rgb(path: Path) -> np.ndarray:
    """PIL 按魔数解码(文件名 .png 实为 JPEG),返回 RGB uint8。"""
    return np.asarray(Image.open(path).convert("RGB"))


def matte(session, rgb: np.ndarray, out_wh: tuple[int, int]) -> np.ndarray:
    """整卡抠像 → float32 alpha(0..1),平滑阶跃硬化边缘。"""
    from rembg import remove
    h0, w0 = rgb.shape[:2]
    im = Image.fromarray(rgb).resize((MATTE_W, round(h0 * MATTE_W / w0)), Image.LANCZOS)
    a = np.asarray(remove(im, session=session))[:, :, 3]
    a = cv2.resize(a, out_wh, interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
    t = np.clip((a - 0.35) / 0.30, 0.0, 1.0)          # smoothstep(0.35, 0.65)
    return t * t * (3.0 - 2.0 * t)


def clean_alpha(a: np.ndarray) -> np.ndarray:
    """去孤岛(免得碎屑跟着前景飘)、填针孔;大的镂空(拱窗)按面积阈值保留。"""
    h, w = a.shape
    lim = int(SPECK * h * w)
    solid = (a >= 0.5).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(solid, 8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < lim:
            a[lab == i] = 0.0
    n, lab, stats, _ = cv2.connectedComponentsWithStats(1 - solid, 8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < lim:
            a[lab == i] = 1.0
    return a


def harden_alpha(raw: np.ndarray, base: np.ndarray) -> tuple[np.ndarray, float]:
    """近二值化 + 不稳定/假分裂区整块归并 + 2px 抗锯齿边;返回 (alpha, 归并面积占比)。

    逐像素 0.5 阈值下,抠像模型在纹样密集区有两种失效形态,都会把一块语义完整的
    浮雕切给两层(静止合成断言天然抓不到,倾斜时才现形):
      1) 摇摆中间值(半透明大区,倾斜=重影):找"成片"中间值——CLOSE(7) 连片、
         腐蚀掉细抗锯齿边带,幸存大块即是;
      2) 双峰碎裂(笔画≈1/底面≈0 交错,如 hysilens 铭牌符文被判空、倾斜=底面滑移):
         逐像素都"自信",中间值探测失明;判据须看内容——空侧连通域的颜色与
         "窗景参照域"(最大空侧连通域=拱窗场景)比:像窗景 → 真镂空,保留分层
         (这正是景深所在);不像窗景(亮色板面) → 假分裂,整块划归前景。
    归并区物理上均属边框纹样/贴片,归前景;背景在其下会被修补。"""
    solid = (raw >= 0.5).astype(np.uint8)
    forced_mask = np.zeros_like(solid)
    basef = base.astype(np.float32)

    # 形态 1:成片摇摆中间值(半透明两可,直接归并,无需内容判据)
    amb = ((raw > 0.15) & (raw < 0.85)).astype(np.uint8)
    amb = cv2.morphologyEx(amb, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    core = cv2.erode(amb, np.ones((5, 5), np.uint8), iterations=2)
    if core.any():
        n, lab, stats, _ = cv2.connectedComponentsWithStats(core, 8)
        for i in range(1, n):
            if stats[i, cv2.CC_STAT_AREA] >= AMB_AREA:
                forced_mask[lab == i] = 1

    # 形态 2:窗景区几何仲裁。这批卡的语义:真背景=拱窗内场景。
    # 参照集 = ≥4% 画布且"不像边框色"的空侧大域(边框色取画布外沿实心中位色;
    # isnet 会把整片卡面误判为空,这类假空域 ≈ 边框色,必须排毒,否则自我豁免);
    # 窗景区 = 参照域膨胀 ~24px。区外的空侧域颜色不像任何参照 → 归前景;
    # 区内(蕾丝/发隙/星屑,景深所在)一律保留。OPEN(5) 先斩细颈防串域。
    empty_open = cv2.morphologyEx((1 - solid), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(empty_open, 8)
    zone = None
    if n > 1:
        areas = stats[:, cv2.CC_STAT_AREA]
        h_, w_ = solid.shape
        m = max(8, round(0.05 * w_))
        border = np.zeros_like(solid, bool)
        border[:m, :] = border[-m:, :] = True
        border[:, :m] = border[:, -m:] = True
        frame_col = np.median(basef[solid.astype(bool) & border], axis=0)
        cols = {i: np.median(basef[lab == i], axis=0) for i in range(1, n) if areas[i] >= 400}
        big = [i for i in cols if areas[i] >= 0.04 * solid.size]
        refs = [i for i in big if np.linalg.norm(cols[i] - frame_col) > 60.0]
        if not refs and big:
            refs = [max(big, key=lambda i: float(np.linalg.norm(cols[i] - frame_col)))]
        if refs and areas[refs[0]] >= 0.03 * solid.size:
            ref_mask = np.isin(lab, refs).astype(np.uint8)
            zone = cv2.dilate(ref_mask, np.ones((5, 5), np.uint8), iterations=6).astype(bool)
            for i in cols:
                if i in refs:
                    continue
                comp = lab == i
                if zone[comp].mean() > 0.5:
                    continue                      # 主体在窗景区内:保留分层
                if min(float(np.linalg.norm(cols[i] - cols[r])) for r in refs) > 90.0:
                    forced_mask[lab == i] = 1
        # 卡片解剖学:底部铭牌横带(题名牌位)。完全落在带内的空侧域不可能是天空
        # ——真背景域都从上方延伸进带,不会被整包含;铭牌底面与背景同色时
        # 颜色/几何判据双双失明(hysilens),唯此先验可断。
        band_y0, band_y1 = 0.85 * h_, 0.985 * h_
        for i in range(1, n):
            if areas[i] < 200:
                continue
            top, hh = stats[i, cv2.CC_STAT_TOP], stats[i, cv2.CC_STAT_HEIGHT]
            if top >= band_y0 and top + hh <= band_y1:
                forced_mask[lab == i] = 1

    forced = 0.0
    if forced_mask.any():
        region = cv2.dilate(forced_mask, np.ones((5, 5), np.uint8), iterations=4)
        solid[region > 0] = 1
        forced = float(region.mean())

    # 窗景区之外的细缝(≤7px:铭牌符文刻缝、OPEN 残余马赛克)一律并入前景——
    # 这些缝里不是天空,倾斜时留在背景只会碎裂滑移;窗景区之内原样保留景深。
    closed = cv2.morphologyEx(solid, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    if zone is not None:
        solid = np.where(zone, solid, closed).astype(np.uint8)
    else:
        solid = closed
    a = cv2.GaussianBlur(solid.astype(np.float32), (5, 5), 0.8)
    # 构造性保证:中间值只能以边带形式存在。窄缝(4-6px)两侧边带叠合会留下少量"厚"像素,
    # 属微观抗锯齿、无重影风险;失效形态(铭牌级成片斑块)是数千到数万像素,阈值取 3000。
    semi_core = cv2.erode(((a > 0.02) & (a < 0.98)).astype(np.uint8),
                          np.ones((7, 7), np.uint8))
    if int(semi_core.sum()) > 3000:
        raise RuntimeError(f"半透明成片区残留 {int(semi_core.sum())}px,归并失效")
    return a, forced


def crest_alpha(shape: tuple[int, int], cx: float, cy: float, r: float) -> np.ndarray:
    """全幅圆片 alpha:半径 r 内为 1,1.5px 线性羽化。"""
    h, w = shape
    d = np.zeros((h, w), np.float32)
    x0, x1 = max(0, int(cx - r - 4)), min(w, int(cx + r + 5))
    y0, y1 = max(0, int(cy - r - 4)), min(h, int(cy + r + 5))
    yy, xx = np.mgrid[y0:y1, x0:x1]
    dist = np.hypot(xx - cx, yy - cy)
    d[y0:y1, x0:x1] = np.clip((r - dist) / 1.5 + 1.0, 0.0, 1.0)
    return d


def inpaint_hidden(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """两段修补:低分辨率 TELEA 铺底(深处永不露出),全分辨率只精修 26px 边缘带。"""
    h, w = mask.shape
    sw = 256
    sh = max(1, round(h * sw / w))
    small = cv2.resize(rgb, (sw, sh), interpolation=cv2.INTER_AREA)
    msmall = cv2.dilate(cv2.resize(mask, (sw, sh), interpolation=cv2.INTER_NEAREST),
                        np.ones((3, 3), np.uint8))
    coarse = cv2.inpaint(small, msmall, 5, cv2.INPAINT_TELEA)
    up = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_CUBIC)
    out = rgb.copy()
    out[mask > 0] = up[mask > 0]
    band = cv2.bitwise_and(mask, cv2.dilate(255 - mask, np.ones((3, 3), np.uint8), iterations=26))
    return cv2.inpaint(out, band, 7, cv2.INPAINT_TELEA)


def shift(img: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """边缘复制式平移(QA 模拟用;np.roll 的环绕会在拼图边缘制造假露馅)。"""
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(img, m, (img.shape[1], img.shape[0]),
                          flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)


def over(dst: np.ndarray, rgb: np.ndarray, a: np.ndarray) -> np.ndarray:
    """dst ← rgb OVER dst(float 合成)。"""
    return rgb * a[..., None] + dst * (1.0 - a[..., None])


def composite(back, front_rgb, front_a, crest_rgb, crest_a,
              d_back=(0, 0), d_crest=(0, 0)) -> np.ndarray:
    """三层合成;d_* 为(dx, dy)整像素平移,用于模拟倾斜视差做 QA。"""
    out = back.astype(np.float32)
    if d_back != (0, 0):
        out = shift(out, *d_back)
    out = over(out, front_rgb.astype(np.float32), front_a)
    ca, cr = crest_a, crest_rgb.astype(np.float32)
    if d_crest != (0, 0):
        ca, cr = shift(ca, *d_crest), shift(cr, *d_crest)
    return np.clip(over(out, cr, ca) + 0.5, 0, 255).astype(np.uint8)


def save_webp(path: Path, rgb: np.ndarray, a: np.ndarray | None, q: int) -> None:
    if a is None:
        Image.fromarray(rgb).save(path, quality=q, method=6)
    else:
        im = np.dstack([rgb, np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)])
        # exact=True 保留透明区 RGB(=原图背景),GPU 双线性采样边缘不出黑边
        Image.fromarray(im).save(path, quality=q, method=6, exact=True)


def verify_encoded(k: str, base: np.ndarray, box: tuple[int, int, int, int]) -> tuple[float, float]:
    """解码落盘的三层复跑合成,对原图算 webp 噪声(mean / p99.9),超阈即抛错。"""
    H, Wd = base.shape[:2]
    back = np.asarray(Image.open(LAYERS / f"{k}-back.webp").convert("RGB"), dtype=np.float32)
    fr = np.asarray(Image.open(LAYERS / f"{k}-front.webp").convert("RGBA"), dtype=np.float32)
    cr = np.asarray(Image.open(LAYERS / f"{k}-crest.webp").convert("RGBA"), dtype=np.float32)
    out = fr[:, :, :3] * (fr[:, :, 3:] / 255) + back * (1 - fr[:, :, 3:] / 255)
    bx0, by0, bx1, by1 = box
    reg = out[by0:by1, bx0:bx1]
    out[by0:by1, bx0:bx1] = cr[:, :, :3] * (cr[:, :, 3:] / 255) + reg * (1 - cr[:, :, 3:] / 255)
    d = np.abs(out - base.astype(np.float32))
    mean, p999 = float(d.mean()), float(np.percentile(d, 99.9))
    if mean > 6 or p999 > 60:
        raise RuntimeError(f"{k}: 编码后合成偏差过大 mean={mean:.2f} p99.9={p999:.0f}")
    return mean, p999


def process(session, k: str) -> dict:
    t0 = time.time()
    src = load_rgb(SRC / f"{k}.png")
    h0, w0 = src.shape[:2]
    H = round(h0 * W / w0)
    base = np.asarray(Image.fromarray(src).resize((W, H), Image.LANCZOS))

    a_front, forced = harden_alpha(clean_alpha(matte(session, src, (W, H))), base)

    # 徽记圆(在原尺寸上检测,换算到层坐标)
    bgr = cv2.cvtColor(src, cv2.COLOR_RGB2BGR)
    hit = detect(bgr, w0)
    if hit is None:
        raise RuntimeError(f"{k}: 徽记圆检测失败")
    cx, cy, r = (v * W / w0 for v in hit)
    rc = r * CREST_MARGIN
    d = crest_alpha((H, W), cx, cy, rc)

    # 背景层修补掩码:前景实心 ∪ 徽记实心,收缩 1px 保证正视全被盖住
    hidden = ((a_front >= 0.995) | (d >= 0.995)).astype(np.uint8) * 255
    hidden = cv2.erode(hidden, np.ones((3, 3), np.uint8))
    back = inpaint_hidden(base, hidden)

    # 前景挖空孔径比徽记盘小 3.5px:孔连同羽化完全藏在徽记不透明区内,
    # 徽记羽化环处前景保持原 alpha——否则该环上三层混合权重不闭合(残差 d(1-d)Δ)
    d_cut = crest_alpha((H, W), cx, cy, rc - 3.5)
    a_front_cut = a_front * (1.0 - d_cut)

    # 静止合成必须还原原图(分区不变量;容差=0.995 阈值 ×255 + 取整)
    rest = composite(back, base, a_front_cut, base, d)
    diff = cv2.absdiff(rest, base)
    dmax, dmean = int(diff.max()), float(diff.mean())
    if dmax > 3:
        raise RuntimeError(f"{k}: 静止合成偏差 max={dmax}")

    save_webp(LAYERS / f"{k}-back.webp", back, None, 86)
    save_webp(LAYERS / f"{k}-front.webp", base, a_front_cut, 84)
    pad = 3
    bx0, by0 = max(0, round(cx - rc - pad)), max(0, round(cy - rc - pad))
    bx1, by1 = min(W, round(cx + rc + pad)), min(H, round(cy + rc + pad))
    save_webp(LAYERS / f"{k}-crest.webp", base[by0:by1, bx0:bx1], d[by0:by1, bx0:bx1], 88)
    enc_mean, enc_p999 = verify_encoded(k, base, (bx0, by0, bx1, by1))

    # QA 拼图:原图 | 静止合成 | 倾斜模拟(背景+14,+8 徽记-10,-6) | 残差×16
    tilt = composite(back, base, a_front_cut, base, d, d_back=(14, 8), d_crest=(-10, -6))
    heat = np.clip(diff.astype(np.int32) * 16, 0, 255).astype(np.uint8)
    strip = np.hstack([base, rest, tilt, heat])
    Image.fromarray(strip).resize((1800, round(strip.shape[0] * 1800 / strip.shape[1])),
                                  Image.LANCZOS).save(QA / f"{k}.jpg", quality=88)

    print(f"{k:20s} {W}x{H}  crest=({cx:.0f},{cy:.0f} r={rc:.0f})  rest max={dmax} mean={dmean:.4f}  "
          f"enc mean={enc_mean:.2f} p99.9={enc_p999:.0f}  归并={forced*100:.1f}%  {time.time()-t0:.1f}s")
    return {
        "w": W, "h": H,
        "crest": {"x": round(bx0 / W, 5), "y": round(by0 / H, 5),
                  "w": round((bx1 - bx0) / W, 5), "h": round((by1 - by0) / H, 5)},
        "rest_diff": {"max": dmax, "mean": round(dmean, 4)},
        "encoded_diff": {"mean": round(enc_mean, 2), "p99.9": round(enc_p999, 1)},
        "forced_region": round(forced, 5),
    }


def main() -> None:
    from rembg import new_session
    LAYERS.mkdir(parents=True, exist_ok=True)
    QA.mkdir(parents=True, exist_ok=True)
    session = new_session("isnet-general-use")
    manifest = {}
    for k in KEYS:
        manifest[k] = process(session, k)
    (LAYERS / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    geo = {k: {"h": v["h"], "c": [v["crest"]["x"], v["crest"]["y"],
                                  v["crest"]["w"], v["crest"]["h"]]} for k, v in manifest.items()}
    (LAYERS / "geo.js").write_text(
        "/* 由 tools/make_layers.py 生成,勿手改;cards.html 的几何单源 */\n"
        "const GEO=" + json.dumps(geo, separators=(",", ":")) + ";\n", encoding="utf-8")
    print("manifest.json / geo.js 已写出;QA 拼图见 tools/qa_out/")


if __name__ == "__main__":
    main()
