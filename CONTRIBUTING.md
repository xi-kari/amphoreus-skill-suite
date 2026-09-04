# 维护手册(CONTRIBUTING)

本仓库的一切修改都围绕一条原则:**`skills/` 是唯一事实源**,其余(适配层、介绍页数据、README 表格)都是它的投影。改动请从事实源开始,再同步投影。

## 一、改卡:SHA 纪律

卡文(`skills/amphoreus-<hero>/SKILL.md` 或 `persona.md`)**任何一字变更**,按家族验收纪律须:

1. 重跑该卡全部 5 个冻结评测场景(`skills/amphoreus/evals/<hero>.md`,rubric 见同目录);
2. 评分由与改卡方隔离的盲评代理执行,再交叉复核;
3. 失败原样入册,不覆盖、不美化;整改后重跑闭合。

台词类改动另有硬约束:`persona.md` 语音条目必须逐字对齐游戏公开语料(分隔符 U+2022、字符级一致),`validate.py` 内建冻结检查会拦截漂移。

共享文件(`skills/amphoreus/references/common.md` / `relations.md`)或评测卷变更属家族级改动:按沙龙批次(v1.3.0)先例,须 13 卡 65 题全量重跑并复验沙龙专项,不能只重跑单卡。

## 二、本地校验

```bash
# 静态校验:卡 13/13 · 路由清单 18/18 · 13 卷评测 65 场景 · UTF-8/LF
python skills/amphoreus/scripts/validate.py --root skills --wave all
```

预期输出 `amphoreus wave all: PASS`(exit 0)。注意它如实标注 `behavior=not_run_by_static_validator`——静态 PASS 不等于行为评测通过。

## 三、适配层:只改生成器,勿手改产物

`adapters/` 下所有 `.md` 均由 `build.py` 生成(文件头带 GENERATED 标记与来源 SHA):

```bash
python adapters/build.py
```

- 新增目标生态:在 `build.py` 的 `CONVENTION_TARGETS` 追加一行(输出路径 / 工具名 / 安装说明),重跑即可;
- 卡的司职一句话描述在 `HEROES` 表,口径以各卡 `SKILL.md` 为准;
- CI 会重跑 `build.py` 并要求 `git diff --exit-code -- adapters`,手改产物会在 PR 上直接红灯。

## 四、素材管线

| 目录 | 来源与纪律 |
| --- | --- |
| `assets/cards-full/` | patchwiki 原尺寸卡面,**原字节入库**(SHA 校验、零压缩;文件名 `.png` 但内容为 JPEG,浏览器按魔数解码无碍) |
| `assets/cards/` | 400×702 等尺寸缩略 JPG(`tools` 无脚本,由 cards-full 等比 cover 裁切;README 画廊与介绍页网格共用,**必须保持 15 张同尺寸**,否则画廊排版会大小不一) |
| `assets/symbols/` | 15 枚徽记,由 `tools/crop_symbols.py` 对 cards-full 做 HoughCircles 圆检测裁切(勿再用旧固定常数) |
| `assets/stickers/` | 官方 Q 版表情包 96 枚:`<key>.png` 存档件(首批 18 枚原字节;2026-09-02 批次 78 枚经 `tools/make_stickers.py` 归一化,最长边 ≤ 512,原图 ≤ 512 者原字节)+ `w/<key>.webp` 显示件(256,q88,三页与 README 只引显示件)+ `manifest.js` / `manifest.json` 清单(owner / label / note / kind / batch)。键名为 ASCII(`tribbie-ning`=缇宁、`march7th-evernight-*`=长夜月、`chimera-<hero>`=奇美拉、`mimi-*`=迷迷、`cyrene-young-*`=小昔涟);新增表情只改脚本 `MAP` 后重跑,`--check` 回对清单与文件一一对应、无孤儿 |
| `assets/layers/` + `cards.html` | 闪卡画廊生产素材:`tools/make_layers.py` 生成三层互斥分区(背景 / 前景 / 徽记,逐卡断言)+ `geo.js` 几何单源;正面合成须逐像素等于原图,改层后用 `cards.html` 的 `?pose` / `?solo` / `?explode` 钩子自检 |

## 五、介绍页(index.html)

- 单文件静态页,无构建;本地预览:`python -m http.server 8917 --directory .`;
- 卡面轮播与十三卡网格的展示顺序由页尾 `<script>` 里的 **`ORDER` 数组唯一决定**(0–14,双开拓者只进轮播与总路由区),改序只改这一处;
- 页面上的验收数字须与 `docs/` 文书一致;气泡台词是贴合各卡话术契约的风格创作,**不得标注为游戏原句**;
- 改动后请至少验证:控制台无报错、移动端(≤560px)无横向溢出、方法卡弹窗可开合、`#card-<key>` 深链可达。

## 六、提交与版本

- 提交信息:中文一行式,先说做了什么、再说范围,与既有历史风格一致;
- 版本:语义化版本,变更记入 `CHANGELOG.md`,发布时打 `v<x.y.z>` 标签;
- GitHub Pages 从 `main` 分支根目录发布(`.nojekyll` 已就位),推送 `main` 即上线。

## 七、素材版权与下架

卡面、徽记、表情包与台词素材版权归米哈游(HoYoverse)所有,本仓库为非商业同人研究用途;LICENSE(MIT)仅覆盖原创代码与文档,不覆盖上述素材。收到有效的版权异议(用 Issue 模板「素材版权 / 下架请求」)时,优先移除对应素材。
