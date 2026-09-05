# 表情索引

按当前实际发言者选图；所属角色组不代表图中人物。三月七与长夜月、缇宝与缇安／缇宁、昔涟与小昔涟分别选择，伙伴也有独立身份。是否显示及数量服从 [共享合同](common.md#对话表情)。

缇宝卡的三声部教学标题表示受众层级，未让姐妹分别出场时，整卡收尾使用缇宝形象；若缇安或缇宁被明确点名出场、冠名发言，紧随该发言的图片只用她本人，不凭教学标题切换人物。

从当前已加载的 `amphoreus` 目录运行 `scripts/stickers.py`；角色卡位于其同级目录。把脚本返回的完整 Markdown 放入回复，可获得经过文件存在检查的绝对路径。

```text
python "<amphoreus目录>/scripts/stickers.py" --speaker 昔涟 --mood 收到
python "<amphoreus目录>/scripts/stickers.py" --speaker 长夜月 --key march7th-evernight-warning
python "<amphoreus目录>/scripts/stickers.py" --speaker 缇安 --list --format json
```

`--speaker` 接受下列英文键、中文名或列出的别名。`--key` 必须是本人的精确键；`--mood` 按本人标签精确匹配；两者与 `--list` 互斥。不指定选择参数时用本人默认图，情绪无匹配或图片缺失时尝试本人默认图，默认图也缺失则省略。伙伴没有基础头像时使用表中本人的代表图。

默认格式为 `markdown`；`json` 返回 `status`、`reason`、`speaker`、`key`、`path`、`markdown`。成功为 `ok`，回退为 `fallback`，资源缺失为 `omitted`，输入错误为 `error`；输入错误退出码为 2，其余为 0。`--list` 返回本人实际存在的图片列表，不自动展示整组图片。

无法运行脚本时，可从本表精确键定位当前 `amphoreus/assets/stickers/<key>.webp`，用可用的文件工具确认存在并取得绝对路径，再写 `![角色·表情](<绝对路径>)`；无法核实就省略。客户端不支持本地图片时只保留文字，不使用开发机路径或猜测远程地址。

| 实际发言者 | 英文键／别名 | 默认图精确键 | 其他表情：精确键 |
|---|---|---|---|
| 阿格莱雅 | aglaea | aglaea | 不：aglaea-no；慷慨：aglaea-generous；泡澡：aglaea-bath；设计：aglaea-design |
| 那刻夏 | anaxa | anaxa | 什么事：anaxa-what；我没事：anaxa-im-fine；来吧：anaxa-bring-it；看穿：anaxa-see-through |
| 遐蝶 | castorice | castorice | 不了：castorice-no-thanks；创作：castorice-create；枯萎：castorice-wither；脸红：castorice-blush；蝴蝶：castorice-butterfly |
| 刻律德菈 | cerydra | cerydra | 公平：cerydra-fair；再说一遍：cerydra-say-again；否决：cerydra-veto；将军：cerydra-checkmate |
| 赛飞儿 | cipher | cipher | 可爱：cipher-cute；得手：cipher-gotcha；招财：cipher-fortune；拜托：cipher-please |
| 昔涟 | cyrene | cyrene | 回眸：cyrene-glance；守护：cyrene-guard；收到：cyrene-roger；爱：cyrene-love |
| 风堇 | hyacine | hyacine | 喜欢：hyacine-like；治愈：hyacine-heal；诊断：hyacine-diagnose；试试看：hyacine-try |
| 海瑟音 | hysilens | hysilens | 共舞：hysilens-dance；哼歌：hysilens-humming；嘘：hysilens-shh；忠诚：hysilens-loyalty |
| 三月七 | march7th | march7th | — |
| 长夜月 | march7th-evernight／evernight | march7th-evernight | 去吧：march7th-evernight-go；嚎啕大哭：march7th-evernight-wail；暗示：march7th-evernight-hint；警告：march7th-evernight-warning |
| 万敌 | mydei | mydei | 健身：mydei-workout；吃什么：mydei-what-to-eat；狂：mydei-frenzy；红温：mydei-flushed |
| 白厄 | phainon | phainon | 再见：phainon-bye；我吗：phainon-me；战斗：phainon-fight；掉线：phainon-offline；没事：phainon-fine；诶嘿：phainon-ehe |
| 丹恒 | terrae／丹恒•腾荒／丹恒·腾荒／丹恒腾荒／dan-heng | terrae | 倾听：terrae-listen；大地之王：terrae-king-of-earth；拍照：terrae-photo；欲言又止：terrae-hesitate |
| 开拓者·穹 | trailblazer-caelus／穹／开拓者男／caelus | trailblazer-caelus | 记录：trailblazer-caelus-record；重写：trailblazer-caelus-rewrite |
| 开拓者·星 | trailblazer-stelle／星／开拓者女／stelle | trailblazer-stelle | 记录：trailblazer-stelle-record；重写：trailblazer-stelle-rewrite |
| 缇宝 | tribbie | tribbie | 炸飞：tribbie-boom；睿智：tribbie-wise |
| 缇安 | tribbie-an | tribbie-an | 晚安：tribbie-an-goodnight |
| 缇宁 | tribbie-ning | tribbie-ning | 发送：tribbie-ning-send |
| 蜜果羹 | chimera-mydei | chimera-mydei | — |
| 暖龙龙 | chimera-terrae | chimera-terrae | — |
| 奇兽爵 | chimera-cerydra | chimera-cerydra | — |
| 咕噜鱼儿 | chimera-hysilens | chimera-hysilens | — |
| 比格椰 | chimera-phainon | chimera-phainon | — |
| 苹果糖 | chimera-tribbie | chimera-tribbie | — |
| 喵咪神偷 | chimera-cipher | chimera-cipher | — |
| 蝶糕糕 | chimera-castorice | chimera-castorice | — |
| 努努斯 | chimera-anaxa | chimera-anaxa | — |
| 胶糖卷 | chimera-march7th | chimera-march7th | — |
| 燕麦粥 | chimera-aglaea | chimera-aglaea | — |
| 车厘比斯 | chimera-hyacine | chimera-hyacine | — |
| 小昔涟 | cyrene-young | cyrene-young-hehe | — |
| 迷迷 | mimi | mimi-hug | 哭：mimi-cry；心心：mimi-hearts；我来：mimi-my-turn；攻击：mimi-attack；睡觉：mimi-sleep |
