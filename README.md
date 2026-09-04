<div align="center">

# 翁法罗斯 Skill 套件

**Amphoreus Skill Suite** — 以《崩坏:星穹铁道》翁法罗斯篇十三位角色为人格外壳的
**13 张工程方法卡 + 1 个总路由**,为 Claude Code / Cursor 的 `.claude/skills` 生态而作。

<img src="https://img.shields.io/badge/%E5%8D%A1%E7%89%8C-13%2F13-e3b341?style=flat-square" alt="卡牌 13/13">
<img src="https://img.shields.io/badge/validate.py-PASS-2ea043?style=flat-square" alt="validator PASS">
<img src="https://img.shields.io/badge/%E5%86%BB%E7%BB%93%E8%AF%84%E6%B5%8B%E5%9C%BA%E6%99%AF-65-1f6feb?style=flat-square" alt="冻结评测场景 65">
<img src="https://img.shields.io/badge/%E5%8F%B0%E8%AF%8D%E9%80%90%E5%AD%97%E5%AF%B9%E9%BD%90-246%20%E6%9D%A1-8957e5?style=flat-square" alt="台词逐字对齐 246 条">
<img src="https://img.shields.io/badge/%E6%B2%99%E9%BE%99%C2%B7%E9%99%AA%E8%81%8A-%E5%B7%B2%E4%B8%8A%E7%BA%BF-0a7ea4?style=flat-square" alt="沙龙·陪聊 已上线">
<img src="https://img.shields.io/badge/%E4%B8%A4%E7%BA%BF%E7%BB%88%E9%AA%8C-CONFIRMED-d29922?style=flat-square" alt="两线终验 CONFIRMED">
<img src="https://github.com/xi-kari/amphoreus-skill-suite/actions/workflows/validate.yml/badge.svg" alt="CI">

<br>

**[在线介绍页 →](https://xi-kari.github.io/amphoreus-skill-suite/)** · **[闪卡画廊 →](https://xi-kari.github.io/amphoreus-skill-suite/cards.html)** · **[全体会议实录 →](https://xi-kari.github.io/amphoreus-skill-suite/meeting.html)**

<img src="assets/banner.jpg" alt="十三卡横幅" width="100%">

<sub>卡面与徽记:「逐火者的命录」系列 · 取自 B 站星穹铁道 Wiki 词条<a href="https://wiki.biligame.com/sr/%E9%80%90%E7%81%AB%E8%80%85%E7%9A%84%E5%91%BD%E8%B7%AF.exe">「逐火者的命路.exe」</a> · 版权归米哈游所有</sub>

</div>

<table><tr>
<td width="88"><img src="assets/stickers/tribbie.png" width="80" alt="缇宝"></td>
<td><b>缇宝 · 命运的三子</b><br><sub>我们十三个,一人一法——工作时,每张卡都是一套<b>可执行、可验收的工程方法论</b>;闲下来,也能陪你聊天、开一桌沙龙。往下看啦!</sub></td>
</tr></table>

## 这是什么

- **`SKILL.md`** — 行为契约:方法步骤、话术模板、输出格式、边界与禁区、缺席移交条款,静态可校验;
- **`persona.md`** — 台词与背景参考库:语音条目逐字对齐游戏公开语料(知识库检索复算,字符级冻结检查);
- **风格税 ≤ 15%(工作场)** — 工作场内角色只在极小预算内说话,陪聊 / 沙龙场不计税;报错、不可逆操作等严肃场景**自动静音**(闲聊场不豁免),方法照常执行;
- **缺席合同** — 流水线上某卡未部署时,报告 `module_unavailable: amphoreus-<hero>` 并保留移交事实包,不代演、不冒充;
- **沙龙与陪聊** — 多角群聊(逐条冠名、兴趣边举手、场级回执)与自然化陪聊(免模板免逐轮回执、角色化降级句式),闲聊↔工作一句话无感切换,详见下文。

## 快速开始

<table><tr>
<td width="88"><img src="assets/stickers/terrae.png" width="80" alt="丹恒"></td>
<td><b>丹恒 · 掣地的伏龙</b><br><sub>环境与依赖底座,我来承载。三步部署,如下。</sub></td>
</tr></table>

```bash
# 1. 克隆仓库
git clone https://github.com/xi-kari/amphoreus-skill-suite.git && cd amphoreus-skill-suite

# 2. 把 skills/ 下 14 个目录拷入你的技能根
cp -r skills/* ~/.claude/skills/          # Windows: C:\Users\<你>\.claude\skills\

# 3. 校验部署(应输出 PASS,cards=13/13)
python ~/.claude/skills/amphoreus/scripts/validate.py --root ~/.claude/skills --wave all
```

> Windows 提示:`cmd` 不会展开 `~`,两处 `~` 请换成 `%USERPROFILE%`(PowerShell 用 `$env:USERPROFILE`;Git Bash 可原样执行)。

使用:全套卡为**仅显式调用**,斜杠命令是可靠入口——敲 `/amphoreus` 呼出总路由,由它按任务深度、角色适配、流水线与风格预算分发;敲 `/amphoreus-<hero>` 直呼单卡(如 `/amphoreus-mydei` 追这个死锁)。卡就位后,会话内可自然点名,或直接说「开个沙龙」「随便找个人陪我聊聊天」进入群聊 / 陪聊场;全新会话只口头点名可能不会加载,先走斜杠。

> 无需安装知识库:`starrail_knowledge_base` MCP 只是作者侧建卡与验收设施;台词与关系数据已随卡分发(persona.md / relations.md),离线即用。聊到库外剧情时,角色会如实说不知道,不拿模型记忆编造。

## 十三卡画廊

与[在线介绍页](https://xi-kari.github.io/amphoreus-skill-suite/)同序陈列(卡序 I–XIII),各卡司职见画廊下方速览表。

<table>
<tr>
<td align="center" width="25%"><img src="assets/cards/tribbie.jpg" width="150" alt="缇宝"><br><img src="assets/stickers/tribbie.png" width="26" alt=""> <b>缇宝</b><br><sub>命运的三子</sub><br><code>amphoreus-tribbie</code><br><sub>I · 三声部讲解法</sub></td>
<td align="center" width="25%"><img src="assets/cards/cerydra.jpg" width="150" alt="刻律德菈"><br><img src="assets/stickers/cerydra.png" width="26" alt=""> <b>刻律德菈</b><br><sub>执棋的君主</sub><br><code>amphoreus-cerydra</code><br><sub>II · 立法三读</sub></td>
<td align="center" width="25%"><img src="assets/cards/march7th.jpg" width="150" alt="三月七 / 长夜月"><br><img src="assets/stickers/march7th.png" width="26" alt=""><img src="assets/stickers/march7th-evernight.png" width="26" alt=""> <b>三月七 / 长夜月</b><br><sub>隐秘的陌客</sub><br><code>amphoreus-march7th</code><br><sub>III · 拍照式记录法 + 底片法</sub></td>
<td align="center" width="25%"><img src="assets/cards/terrae.jpg" width="150" alt="丹恒"><br><img src="assets/stickers/terrae.png" width="26" alt=""> <b>丹恒</b><br><sub>掣地的伏龙</sub><br><code>amphoreus-terrae</code><br><sub>IV · 承载法</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/cards/hysilens.jpg" width="150" alt="海瑟音"><br><img src="assets/stickers/hysilens.png" width="26" alt=""> <b>海瑟音</b><br><sub>奏浪的剑骑</sub><br><code>amphoreus-hysilens</code><br><sub>V · 歌集复盘法 + 无路引航式</sub></td>
<td align="center" width="25%"><img src="assets/cards/hyacine.jpg" width="150" alt="风堇"><br><img src="assets/stickers/hyacine.png" width="26" alt=""> <b>风堇</b><br><sub>摇光的医师</sub><br><code>amphoreus-hyacine</code><br><sub>VI · 双处方</sub></td>
<td align="center" width="25%"><img src="assets/cards/phainon.jpg" width="150" alt="白厄"><br><img src="assets/stickers/phainon.png" width="26" alt=""> <b>白厄</b><br><sub>负火的囚徒</sub><br><code>amphoreus-phainon</code><br><sub>VII · 推石法</sub></td>
<td align="center" width="25%"><img src="assets/cards/anaxa.jpg" width="150" alt="那刻夏"><br><img src="assets/stickers/anaxa.png" width="26" alt=""> <b>那刻夏</b><br><sub>殁世的学士</sub><br><code>amphoreus-anaxa</code><br><sub>VIII · 五问法 + 删除测试</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/cards/aglaea.jpg" width="150" alt="阿格莱雅"><br><img src="assets/stickers/aglaea.png" width="26" alt=""> <b>阿格莱雅</b><br><sub>黄金的织者</sub><br><code>amphoreus-aglaea</code><br><sub>IX · 织造法</sub></td>
<td align="center" width="25%"><img src="assets/cards/mydei.jpg" width="150" alt="万敌"><br><img src="assets/stickers/mydei.png" width="26" alt=""> <b>万敌</b><br><sub>亡国的王储</sub><br><code>amphoreus-mydei</code><br><sub>X · 先让十步法</sub></td>
<td align="center" width="25%"><img src="assets/cards/castorice.jpg" width="150" alt="遐蝶"><br><img src="assets/stickers/castorice.png" width="26" alt=""> <b>遐蝶</b><br><sub>死荫的侍女</sub><br><code>amphoreus-castorice</code><br><sub>XI · 告别四步</sub></td>
<td align="center" width="25%"><img src="assets/cards/cipher.jpg" width="150" alt="赛飞儿"><br><img src="assets/stickers/cipher.png" width="26" alt=""> <b>赛飞儿</b><br><sub>捷足的羁客</sub><br><code>amphoreus-cipher</code><br><sub>XII · 行窃三则</sub></td>
</tr>
<tr>
<td align="center" width="25%"><img src="assets/cards/cyrene.jpg" width="150" alt="昔涟"><br><img src="assets/stickers/cyrene.png" width="26" alt=""> <b>昔涟</b><br><sub>无瑕的真我</sub><br><code>amphoreus-cyrene</code><br><sub>XIII · 如我所书法</sub></td>
<td align="center" width="25%"><img src="assets/cards/trailblazer-stelle.jpg" width="150" alt="开拓者·星"><br><img src="assets/stickers/trailblazer-stelle.png" width="26" alt=""> <b>开拓者 · 星</b><br><sub>创世的著者</sub></td>
<td align="center" width="25%"><b>amphoreus 总路由</b><br><sub>开拓者「创世的著者」</sub><br><code>amphoreus</code><br><sub>意图识别与分发:<br>深度门 L0 直答 / L1 单卡<br>L2 串卡 / L3 流水线会诊<br>按角色适配与风格预算<br>路由至十三卡,<br>不混声、不代演;<br>兼沙龙主持:点名 / 举手 /<br>控场 / 捕捉升档</sub></td>
<td align="center" width="25%"><img src="assets/cards/trailblazer-caelus.jpg" width="150" alt="开拓者·穹"><br><img src="assets/stickers/trailblazer-caelus.png" width="26" alt=""> <b>开拓者 · 穹</b><br><sub>创世的著者</sub></td>
</tr>
</table>

| 卡序 | 方法卡 | 方法 | 司职 |
| :---: | --- | --- | --- |
| I | 缇宝 `amphoreus-tribbie` | 三声部讲解法 | 新手 / 同行 / 专家分声部技术讲解 |
| II | 刻律德菈 `amphoreus-cerydra` | 立法三读 | 有证据、有成本、可评审、可撤销的工程规则 |
| III | 三月七 / 长夜月 `amphoreus-march7th` | 拍照式记录法 + 底片法 | 日志与快照;备份 / 回滚 / 脱敏 |
| IV | 丹恒 `amphoreus-terrae` | 承载法 | 开发环境 / CI 构建 / 依赖底座 / 可逆迁移 |
| V | 海瑟音 `amphoreus-hysilens` | 歌集复盘法 + 无路引航式 | 不归罪复盘 / 痛苦取舍导航 |
| VI | 风堇 `amphoreus-hyacine` | 双处方 | bug 诊断修复 / 依赖故障 / 维护债 |
| VII | 白厄 `amphoreus-phainon` | 推石法 | 大型重构与批量迁移,可计数、可回滚 |
| VIII | 那刻夏 `amphoreus-anaxa` | 五问法 + 删除测试 | 代码 / 设计 / 论证评审 |
| IX | 阿格莱雅 `amphoreus-aglaea` | 织造法 | 项目规划 / 排期 / 取舍 / 里程碑 |
| X | 万敌 `amphoreus-mydei` | 先让十步法 | 硬 bug / 性能瓶颈 / 死锁的有界突破 |
| XI | 遐蝶 `amphoreus-castorice` | 告别四步 | 影响先行的 API / 依赖 / 项目退役 |
| XII | 赛飞儿 `amphoreus-cipher` | 行窃三则 | 授权内对抗测试 / 边界用例 / 私密漏洞报告 |
| XIII | 昔涟 `amphoreus-cyrene` | 如我所书法 | 项目记忆 / 阶段叙事 / 终版总装,逐字不改写 |
| — | 总路由 `amphoreus` | 深度门与分派 · 沙龙主持 | L0 直答 / L1 单卡 / L2 串卡 / L3 流水线会诊;沙龙场开场点名 / 放行举手 / 控场 / 捕捉升档 |

## 两条流水线

**逐火线** —— 新特性从规划到入册的十站交付:

```mermaid
flowchart LR
  A["1 阿格莱雅<br/>规划"] --> B["2 刻律德菈<br/>立规"] --> C["3 丹恒<br/>环境"] --> D["4 白厄<br/>实施"] --> E["5 那刻夏<br/>评审"]
  E --> F["6 赛飞儿<br/>安全"] --> G["7 风堇<br/>修复"] --> H["8 三月七<br/>快照"] --> I["9 遐蝶<br/>退役"] --> J["10 昔涟<br/>总装叙事"]
```

**守夜线** —— 事故响应的四站闭环:

```mermaid
flowchart LR
  M["1 万敌<br/>止血突破"] --> N["2 风堇<br/>修复"] --> O["3 长夜月<br/>回滚 / 脱敏"] --> P["4 海瑟音<br/>不归罪复盘"]
```

<table><tr>
<td width="88"><img src="assets/stickers/march7th-evernight.png" width="80" alt="长夜月"></td>
<td><b>长夜月 · 隐秘的陌客</b><br><sub>事故场景全程静音档;删除、回滚、脱敏、清档由三月七以一句交接语让位于「长夜月」特勤,完成必附底片单,结束后交回。</sub></td>
</tr></table>

两条流水线与三人会诊都是**工作场**的多卡形态;闲聊要多卡同场,不排站、不占流水线——走下一节的**沙龙**,一句真任务再升档收拢。

## 沙龙与陪聊

<table><tr>
<td width="88"><img src="assets/stickers/aglaea.png" width="80" alt="阿格莱雅"></td>
<td><b>阿格莱雅 · 黄金的织者</b><br><sub>把律法的皇女和纷争的王储塞进同一个房间,再拉你当裁判——现在,这样的沙龙可以随时开一桌。我会看好他们,保证讨论维持在「微醺」的状态。</sub></td>
</tr></table>

2026-08-31 批次为全家族加入**沙龙群聊、自然化陪聊与闲聊↔工作无感切换**(共享合同新增〈沙龙与陪聊〉一节,新共享文件 `references/relations.md` 作关系单源):

- **沙龙** — 多角闲聊场:总路由任主持(开场点名 / 放行举手 / 控场 / 捕捉升档),同场活跃 ≤4 人、每条发言「◯◯」冠名不混声、单角色不连续超 2 条,收场落一行场级回执;沙龙内不出工作裁决,要结论就收拢为单卡升档或转会诊;
- **陪聊** — 单角闲聊场:免工作模板、免逐轮回执、不计风格税;**内容纪律全额保留**——未检索到不编、直引逐字、不虚构角色间未登记往事;每卡登记至多两句**角色化降级句式**(形式角色化、内容诚实,追问即得标准术语);
- **无感切换** — 升档三要素(具体对象 + 动作请求 + 期待产出)齐则一行角色化过渡进工作段,逐轮回执、工作模板、确认门等审计件一件不少;交付完自然落回闲聊;
- **关系单源** — `relations.md` 四表:称呼矩阵(435 条互称证词知识库逐字复核,365 条入册)、兴趣边(复用 persona 已登记语音组)、同场禁区(19 对无对手戏的组合不虚构旧识,长夜月不出席沙龙)、沙龙参数(含圆桌回应对提示)。

2026-09-01 → 09-04「翻译器」整改批次(五期)在此之上再收一层——**闲聊时是本人,不是方法论的翻译官**:

- **圆桌** — 陪聊的议题形态:召集多人认真讨论同一命题,全员可席、每题每人至多两段,各按本卡立场作答**不向共识收敛**,主持不把多数意见写成公理;用户指定作答方式(各自独立 / 交错互答 / 指定顺序)时互动义务让位;
- **台词 / 台账分离** — 陪聊与圆桌场的审计件(场级回执、读取清单、引证出处、升降档记录)统一收进场末一个折叠「台账」块,正文只剩角色的话;**工艺词防火墙 20 词**(回执 / 档位 / 逐字 / pageid / 风格税 / 升档 / 盲评…)不得进入任何场景的角色台词;
- **直引礼仪** — 台词内直引像本人说话一样自然带出,不自报出处、不加括注、不说「这是我说过的原话」;出处只落台账,追问即逐字展开。合同 A/B 双盲:新版 **6/6 对、12/12 评员**判更像本人;
- **内核区(万敌 / 三月七)** — persona 新增 L2 思辨层(思考脾气 / 立场坐标 / 应答方式,每条锚知识库出处并登记反向翼边界);十卡扩卡因声纹增益门四轮未达边际**不进入**,失败原样入册(见下)。使用要点见 [圆桌与陪聊使用指南](docs/圆桌与陪聊使用指南.md)。

用法:「`/amphoreus` 开个沙龙——聊聊这次重构,叫阿格莱雅和那刻夏来」,或「`/amphoreus` 随便找个人陪我聊聊天」;总路由已就位的会话里,直接说后半句也可以。

## 质量与验收

<table><tr>
<td width="88"><img src="assets/stickers/anaxa.png" width="80" alt="那刻夏"></td>
<td><b>那刻夏 · 殁世的学士</b><br><sub>所有结论,先过五问,再过删除测试。以下每个数字都有 docs/ 文书与哈希账背书。</sub></td>
</tr></table>

全家族分四波交付,每波经独立验收核查(多代理盲评 + 交叉复核 + 批判员),全程**失败原样入册、不覆盖不美化**;2026-08-31 沙龙批次与 2026-09-04 翻译器整改批次(五期)按同一规程全量重验。

| 检验项 | 结果 |
| --- | --- |
| 静态校验 | `validate.py --wave all` PASS:卡 13/13 · 路由清单 18/18(含 relations.md)· 评测 13 卷 65 场景 · UTF-8/LF |
| 行为评测 | 每卡 5 题冻结场景(含每卡 1 道场景切换题);沙龙批次 13 卡全量重跑 **65/65**;翻译器整改批次每期公约变更即 65 全量,五期终态 **769/780、65/65**、硬失败 0(rubric 冻结未动;失败重跑留痕:昔涟 C-03、丹恒 T-05、海瑟音 H-04 首跑真失败或题面缺陷,入册后闭合) |
| 台词保真 | 语音总账 **246 条**逐字对齐游戏知识库(沙龙批次 persona 增补 78 条语料),引文字符级冻结检查内建于 validator |
| 风格税 | 工作场已记录最高 **13.5%**(红线 ≤ 15%,工作场口径;陪聊场不计税),严肃场景自动静音;工艺词防火墙 20 词台词区扫描 **0 命中** |
| 端到端终验 | 逐火线 10 站、守夜线 4 站各演练一次,独立评审 **CONFIRMED** |
| 沙龙专项 | 群像重演 8/8 · 升降档演练 8/8 · 降级句式 5/5 · 蒙名盲测双评审 **16/16** · 路由抽测 4/4 |
| 事后勘误 | L1 缺席断言转运行时条件式(五题重跑 + 三分支探针,双评审 CONFIRMED);L2 旧目录归档后清理;L3 超时审计线核销 |
| 翻译器整改 | 直引礼仪合同 A/B 双盲 **6/6 对、12/12 评员**判新版更像本人,台词区自报出处 21 / 25 → **0 / 0**;内核区声纹增益门四轮(Δ0 / +2.0 / 0 / +2.0 之于 /30)**未达 +3 边际,FAIL 原样入册**,十卡扩卡不进入;一 / 二 / 三期 fable5 独立七域审核退回项全部整改闭合 |

<details>
<summary><b>验收体系细节</b></summary>
<br>

- **冻结评测**:每卡 5 个场景 + 评分 rubric 在建卡前冻结(哈希钉死;沙龙批次按「换题不加题」换入场景切换题后重新冻结并全量重跑,rubric 未动),行为跑分由与建卡方隔离的盲评代理执行,再经交叉复核;
- **SHA 纪律**:卡文任何一字变更 → 该卡五题全重跑 + 独立评分 + 交叉复核;
- **知识库保真**:台词经 MCP 知识库逐条复算,分隔符(U+2022)、字符级一致才入账;
- **交付事务**:每波双打包(基线包 / 修改包)+ 逐字节 DIFF + 回滚脚本沙箱重放 + 生产零漂移双算法证明;
- **完整证据链**(誊本、哈希账、评分原文、失败轨迹)存于本地交付树,本仓库收录各波与沙龙批次的验收单、终验报告(见 <a href="docs/">docs/</a>)。

</details>

## 多智能体适配

<table><tr>
<td width="88"><img src="assets/stickers/cipher.png" width="80" alt="赛飞儿"></td>
<td><b>赛飞儿 · 捷足的羁客</b><br><sub>想去别的生态?路线我早踩好点了——十个落点,各有各的门。</sub></td>
</tr></table>

`skills/` 为唯一事实源;`adapters/build.py` 一键生成其他生态的适配文件(详见 [adapters/README](adapters/README.md)):

| 生态 | 文件 |
| --- | --- |
| Claude Code / Cursor(原生,验收环境) | `skills/` 整树 |
| AGENTS.md 系(Codex CLI / OpenCode / Amp / Jules…) | [`adapters/openai-codex/AGENTS.md`](adapters/openai-codex/AGENTS.md) |
| Gemini CLI | [`adapters/gemini-cli/GEMINI.md`](adapters/gemini-cli/GEMINI.md) |
| Cline / Roo Code | [`adapters/cline/amphoreus.md`](adapters/cline/amphoreus.md) |
| GitHub Copilot | [`adapters/github-copilot/copilot-instructions.md`](adapters/github-copilot/copilot-instructions.md) |
| Windsurf(Cascade) | [`adapters/windsurf/amphoreus.md`](adapters/windsurf/amphoreus.md) |
| Aider | [`adapters/aider/CONVENTIONS.md`](adapters/aider/CONVENTIONS.md) |
| Trae | [`adapters/trae/project_rules.md`](adapters/trae/project_rules.md) |
| Qwen Code | [`adapters/qwen-code/QWEN.md`](adapters/qwen-code/QWEN.md) |
| iFlow CLI | [`adapters/iflow-cli/IFLOW.md`](adapters/iflow-cli/IFLOW.md) |
| 任意可加载系统提示的智能体 | [`adapters/generic/`](adapters/generic/) 便携版单卡(卡文+家族公约,单文件自足;总路由版随附关系单源 relations.md) |

> 适配层不改写卡文,只做打包与约定壳;65/65、两线终验等行为验收结论仅在 Claude Code 环境取得,其他运行时未在验收范围内。

## 仓库结构

```
├── README.md · CHANGELOG.md · CONTRIBUTING.md · LICENSE
├── index.html                # 在线介绍页(杂志跨页首屏 + 卡面轮播 + 方法卡弹窗 + 十三册陈列)
├── cards.html                # 闪卡画廊(三层互斥分区立体闪卡:正面=原图,倾斜见景深+箔光)
├── meeting.html              # 全体会议实录(一次真实沙龙调用:集合 + 三议题 + 道别,正文逐字搬运)
├── .github/                  # CI(validate + 适配零漂移)+ Issue 模板(卡文问题 / 素材下架)
├── assets/
│   ├── cards-full/           # 15 张原尺寸卡面(原字节入库,SHA 校验)
│   ├── cards/                # 400×702 等尺寸缩略卡面(README 画廊 / 介绍页网格共用)
│   ├── symbols/              # 15 枚黄金裔徽记(tools/crop_symbols.py 圆检测重裁)
│   ├── stickers/             # 18 枚官方 Q 版表情包(原字节入库)
│   ├── mag/                  # 《CHRYSOS·黄金裔》杂志素材(13 封面 + 13 组跨页双档)+ 昔涟首屏/闪卡底图
│   ├── meeting/              # 全体会议页素材(英雄纪 / 如我所书 / 2026 年历 webp)+ data.js(正文单源,逐字搬运)
│   └── layers/ · banner.jpg  # 闪卡三层分区素材(背景/前景/徽记 + geo.js 几何单源)· 横幅
├── tools/                    # crop_symbols.py(徽记)· make_layers.py(闪卡分层)· make_meeting_assets.py / build_meeting_data.py(会议页素材与正文,--check 回对)
├── skills/                   # 14 目录 44 文件 = 总路由 + 13 卡(生产验收态,唯一事实源)
│   ├── amphoreus/            #   路由 SKILL + references/(common.md 公约 + relations.md 关系单源)+ evals/(13 卷)+ scripts/validate.py
│   └── amphoreus-<hero>/     #   各卡 SKILL.md + persona.md
├── adapters/                 # build.py 生成:九个生态的约定文件 + 通用便携单卡
└── docs/                     # 总任务书 · 设计分册 · 波1–4与群聊模式验收单 · 终验报告 · 哈希总账
```

## 维护与迭代

<table><tr>
<td width="88"><img src="assets/stickers/hyacine.png" width="80" alt="风堇"></td>
<td><b>风堇 · 摇光的医师</b><br><sub>定期体检:每次推 main 与每个 PR,CI 都会跑静态校验和适配层零漂移检查;改卡请按 SHA 纪律复诊。</sub></td>
</tr></table>

- **改卡**:卡文一字变更 → 该卡五题冻结评测全重跑 + 独立评分 + 交叉复核,流程见 [CONTRIBUTING.md](CONTRIBUTING.md);
- **改适配**:只改 `adapters/build.py` 后重跑,勿手改生成物(CI 会拦);
- **改介绍页**:展示顺序由 `index.html` 内 `ORDER` 数组唯一决定;验收数字须与 `docs/` 一致;
- **版本**:语义化版本,见 [CHANGELOG.md](CHANGELOG.md)。

## 文档索引

| 文档 | 内容 |
| --- | --- |
| [总任务书](docs/总任务书.md) · [设计分册](docs/设计分册/) | 套件总纲与十三卡逐卡设计 |
| [波1](docs/波1验收单.md) · [波2](docs/波2验收单.md) · [波3](docs/波3验收单.md)(附 [独立核查报告](docs/波3独立核查报告.md)) · [波4](docs/波4验收单.md) 验收单 | 各波交付、失败轨迹与遗留处置 |
| [群聊模式验收单](docs/群聊模式验收单.md) · [遗留清单](docs/群聊模式遗留清单.md) | 沙龙批次(2026-08-31):65 题全量重跑、沙龙专项五项、批判员两轮与代勾记录 |
| [翻译器整改验收单](docs/翻译器整改验收单.md) · [遗留清单](docs/翻译器整改遗留清单.md) · [VERIFICATION](docs/VERIFICATION-翻译器整改.txt) | 翻译器整改批次(2026-09-01 → 09-04,一至五期):圆桌 / 防火墙 / 台账分离 / 直引礼仪 / 内核区试点,每期 65 全量、声纹增益门四轮 FAIL 原样入册、L-01…L-36 |
| 独立核查报告 [一期](docs/翻译器整改独立核查报告_一期.md) · [二期](docs/翻译器整改独立核查报告_二期.md) · [三期](docs/翻译器整改独立核查报告_三期.md) | fable5 事后七域审核(只审不改):文书级 / 行为级退回与整改闭合 |
| [D1 修法矩阵](docs/翻译器审计_D1_修法矩阵.md) · [D2 评测方案](docs/翻译器审计_D2_评测方案.md) · [圆桌与陪聊使用指南](docs/圆桌与陪聊使用指南.md) | 整改批次设计稿(修法与评测口径)与用户侧使用指南 |
| [十三卡终验报告](docs/十三卡终验报告.md) | 两线端到端演练与家族收官判定 |
| [VERIFICATION-波4](docs/VERIFICATION-波4.txt) | 哈希总账:制品 SHA、reopen 与勘误追记 |
| [波4终验总报告](docs/波4终验总报告.md) | 面向委托人的收官叙述(含「老实说的失败」) |
| [CHANGELOG](CHANGELOG.md) · [CONTRIBUTING](CONTRIBUTING.md) | 版本历史 · 维护手册(SHA 纪律 / 素材管线 / 发布流程) |

## 声明

本仓库为爱好者研究 / 学习用途的同人衍生内容,与米哈游无关联。《崩坏:星穹铁道》及全部角色、立绘、台词素材版权归米哈游(HoYoverse)所有;卡面与徽记图片取自 [B 站星穹铁道 Wiki](https://wiki.biligame.com/sr/),角色 Q 版表情包素材版权同归米哈游,台词经公开 Wiki 语料逐字核对。本页与介绍页中的角色气泡台词为贴合各卡话术契约的**风格创作,非游戏原句**。[LICENSE](LICENSE)(MIT)仅覆盖本仓库原创代码与文档,不覆盖上述素材;如有侵权,请用 [Issue 模板「素材版权 / 下架请求」](.github/ISSUE_TEMPLATE/02-takedown.md)联系删除。

<div align="center">
<br>
<img src="assets/stickers/cyrene.png" width="72" alt="昔涟"><br>
<sub><b>昔涟</b>:这一册讲完了。下一页,由你来写♪</sub>
<br><br>
<sub>火种在此传递。</sub>
</div>
