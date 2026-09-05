# 其他智能体适配(Adapters)

`skills/` 是唯一事实源。各生态规则文件、`generic/` 便携卡及其表情资源由 `build.py` 生成,**勿手改生成物**。生成与检查命令:

```bash
python adapters/build.py
python adapters/build.py --check
```

`--check` 不写文件,逐字节检查便携卡、内嵌表情索引、图片清单、WebP 与选图脚本是否和原生文件同步;缺失、内容漂移或多余的旧表情资源会返回非零退出码。默认构建会同步这些文件并清理生成资源目录中的旧文件,可直接用于现有 CI 的重建零漂移检查。

能直接加载 Agent Skills 目录的客户端使用 `skills/` 即可,无需本目录。这里为规则文件或单文件提示词的安装方式提供入口与打包;表情仍共用原生选图脚本、索引和图片,没有各平台专属的图片渲染实现。

## 支持矩阵

| 目标生态 | 取用文件 | 安装方式 |
| --- | --- | --- |
| **Claude Code / Cursor**(原生) | `skills/` 整树 | 拷入 `~/.claude/skills/`,见仓库主 README |
| **OpenAI Codex CLI / OpenCode / Amp / Jules** 等 AGENTS.md 系 | `adapters/openai-codex/AGENTS.md` | 放项目根或全局(如 `~/.codex/AGENTS.md`),连同 `adapters/generic/` 一起携带 |
| **Gemini CLI** | `adapters/gemini-cli/GEMINI.md` | 放项目根或 `~/.gemini/GEMINI.md`,连同 `adapters/generic/` 携带 |
| **Cline / Roo Code** | `adapters/cline/amphoreus.md` | Cline 拷入 `.clinerules/`;Roo Code 拷入 `.roo/rules/`(Roo 不读目录形态的 `.clinerules/`);连同 `adapters/generic/` 携带 |
| **GitHub Copilot** | `adapters/github-copilot/copilot-instructions.md` | 拷为项目 `.github/copilot-instructions.md`,连同 `adapters/generic/` 携带 |
| **Windsurf(Cascade)** | `adapters/windsurf/amphoreus.md` | 拷入项目 `.windsurf/rules/`,连同 `adapters/generic/` 携带 |
| **Aider** | `adapters/aider/CONVENTIONS.md` | 放项目根,`aider --read CONVENTIONS.md` 加载(或写入 `.aider.conf.yml` 的 `read:`),连同 `adapters/generic/` 携带 |
| **Trae** | `adapters/trae/project_rules.md` | 拷为项目 `.trae/rules/project_rules.md`,连同 `adapters/generic/` 携带 |
| **Qwen Code** | `adapters/qwen-code/QWEN.md` | 放项目根或 `~/.qwen/QWEN.md`,连同 `adapters/generic/` 携带 |
| **iFlow CLI** | `adapters/iflow-cli/IFLOW.md` | 放项目根或 `~/.iflow/IFLOW.md`,连同 `adapters/generic/` 携带 |
| **任意可加载系统提示的智能体** | `adapters/generic/amphoreus-<hero>.md`(单卡便携版) | 直接把单卡文件作为 system prompt / 自定义指令加载;本地表情还需部署 `generic/` 资源并允许文件访问 |

> 约定型生态(AGENTS.md / GEMINI.md / Copilot / Windsurf / Aider / Trae / QWEN / IFLOW / Cline)共用同一份约定正文,只是落点与安装方式不同;它们负责"何时召唤哪张卡",实际卡文一律回读 `adapters/generic/` 便携版。

## 便携版单卡的构成

每个 `generic/amphoreus-<hero>.md` 包含生成头(含来源 SHA)、卡文 `SKILL.md` 原文、家族公约 `common.md` 原文及 `references/stickers.md` 表情索引原文。`amphoreus-router.md` 另附关系单源 `relations.md` 原文;台词库 `persona.md` 为可选伴读(工作场角色说话 ≤15% 风格预算,陪聊 / 沙龙场不计税,实际严肃工作段自动静音)。

## 对话中的表情包

保留以下目录关系,并让智能体知道 `generic/` 的实际部署位置:

```text
generic/
├── amphoreus-router.md
├── amphoreus-<hero>.md
├── assets/stickers/
│   ├── manifest.json
│   └── *.webp
└── scripts/stickers.py
```

便携卡壳负责路径映射:文中原生 `amphoreus` 根目录对应当前 `generic/` 根目录,`references/stickers.md` 对应便携卡末尾已内嵌的索引。读取规则、选择当前发言者和表情、静音与数量限制均服从原文中的共享合同。

有 Python 3 和文件工具的宿主可在仓库根运行以下命令;部署到其他位置时使用相应的脚本路径:

```bash
python adapters/generic/scripts/stickers.py --speaker cyrene --mood 收到
python adapters/generic/scripts/stickers.py --speaker 昔涟 --list --format json
```

默认选图结果是带本地图片绝对路径的 Markdown,可直接放进对应角色回复。`--key` 可指定索引中的精确表情键,`--format json` 可供支持结构化结果的宿主读取。脚本仅用 Python 标准库;无法运行脚本但可以读取文件时,按内嵌索引选取已验证存在的图片即可。

图片能否显示由宿主客户端决定。支持本地 Markdown 图片的桌面宿主可直接显示;只读文本的终端、无文件工具的宿主或仅粘贴系统提示的用法会自然省略图片。角色文字与方法仍按合同执行。远程图片只使用用户明确提供且已验证可用的地址,不内置第三方远程回退、不推测图片网址。

## 忠实性说明

适配层不改写任何卡文、共享合同或表情索引内容,只做打包与约定壳;行为契约、缺席条款(`module_unavailable`)、移交事实包纪律与原生版逐字一致。原有验收结论(行为 65/65、两线端到端 CONFIRMED)是在 Claude Code 环境下取得的,不能作为表情显示或其他生态运行效果的验收结果。生成物一致性由构建检查覆盖,实际选图与内嵌显示仍需在各自模型和客户端中验证。

日常聊天的开场、持续对话与告别均只呈现自然话语、必要场面和表情，不自动附台账、回执、读取清单或模式说明。用户主动追问来源或执行情况时只答所问，随后继续自然聊天；明确的工程工作请求按工作合同处理。
